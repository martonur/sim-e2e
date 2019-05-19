#!/usr/bin/env bash

found_map=false
declare -a tracks=("corkscrew" "forza" "ruudskogen" "spring" "street-1" "wheel-1")

# Check if given parameter is a valid map name
for i in "${tracks[@]}"
do
   if [ "$1" = "$i" ]; then
      found_map=true
   fi
done

if [ ! -f /root/.torcs/config/raceman/practice.xml ]; then
      echo "ERROR: Config file not found, run TORCS first and build it if necessary!"

else
   if [ "$found_map" = false ]; then
      echo "ERROR: Map name is not valid, choose one of the listed ones instead: "
      for i in "${tracks[@]}"
      do
          echo "- $i"
      done

   else
      for i in "${tracks[@]}"
      do
         sed -i -e "s/$i/$1/g" /root/.torcs/config/raceman/practice.xml
      done
   echo "Map successfully changed to $1!"
   fi
fi

