find . -type f -name "* *" -print |
while read name; do
na=$(echo $name | tr ' ' '')
if [[ $name != $na ]]; then
mv "$name" "$na"
fi
done