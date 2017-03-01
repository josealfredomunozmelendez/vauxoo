if [[ $(git status --porcelain) ]]; then 

  git commit -m "[ADD] Updated by ${CI_BUILD_REF}" && git push origin master && exit 0

else 

  exit 0 

fi
