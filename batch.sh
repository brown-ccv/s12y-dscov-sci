#!/bin/bash

npm install

rm -rf analyses 
mkdir analyses

for filename in manifests/*;
do
  output_name="analyses/$(basename -- "${filename##*/}")"
  npx if-run -m $filename > $output_name
done

rm -f outputs.csv
echo "id,energy,carbon/operational,carbon/embodied,carbon,sci" > outputs.csv

for filename in analyses/*;
do
  filename_with_ext=${filename##*/}
  jobid=${filename_with_ext%.*}
  data=$(tail -n 7 $filename | head -n 6 | awk -F': *' '{print $2}' | tr '\n' ',' | sed 's/,$//' | sed 's/.\{1\}$//')
  echo "$jobid,$data" >> outputs.csv
done

cat outputs.csv
