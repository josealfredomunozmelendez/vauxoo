FROM quay.io/ruiztulio/odoo-base-image:master
MAINTAINER Tulio Ruiz <tulio@vauxoo.com>
RUN adduser --home=/home/odoo --disabled-password --gecos "" --shell=/bin/bash odoo

RUN echo 'root:odoo' |chpasswd

USER odoo
RUN /bin/bash -c "mkdir -p /home/odoo/instance/{config,extra_addons}"
RUN cd /home/odoo/instance && git clone -b 8.0 --single-branch https://github.com/odoo/odoo.git odoo
RUN cd /home/odoo/instance/extra_addons \
    && git clone -b oml-8-dev-julio --single-branch git@bitbucket.org:julioserna/oml-v2-8-dev-julio.git oml \
    && git clone -b 8.0 git@github.com:vauxoo-dev/cms.git cms \
    && git clone -b 8.0 git@github.com:Vauxoo/odoo-network.git odoo_network \
    && git clone -b 8.0 git@github.com:vauxoo/server-tools.git server_tools\
    && git clone -b 8.0 git@github.com:vauxoo-dev/instance-vauxoo-com.git instance_vauxoo_com \
    && bzr branch lp:addons-vauxoo addons_vauxoo

ADD files/odoo.conf /home/odoo/instance/config/
ADD files/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
RUN mkdir -p /home/odoo/.local/share
ENV XDG_DATA_HOME /home/odoo/.local/share

USER root
RUN mkdir /external_files
ADD files/odoo.conf /external_files/odoo.conf
ADD files/supervisord.conf /external_files/supervisord.conf
ADD files/entry_point.py /entry_point.py
RUN chmod +x /entry_point.py
RUN mkdir -p /var/log/supervisor
VOLUME ["/var/log/supervisor", \
        "/home/odoo/instance/odoo/openerp/filestore", \
        "/home/odoo/instance/odoo/config"]

EXPOSE 8069
CMD /entry_point.py
#ENTRYPOINT ["/entry_point.py"]
