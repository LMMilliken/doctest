temp_dir=$(mktemp -d)
echo "TEMP_DIR=$temp_dir"

cd $temp_dir
git clone <REPO>