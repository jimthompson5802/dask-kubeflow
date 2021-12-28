#/bin/bash

image_tag=${1:-v1}
push_image=${2:-true}

docker build \
  -t dsimages/jupyter-dask:${image_tag} \
  -f Dockerfile_jupyternotebook_with_dask_labextension .

if [[ ${push_image} == true ]]
then
  echo "pushing image with tag ${image_tag}"  \
  && docker push dsimages/jupyter-dask:${image_tag}
fi