#!/usr/bin/env bash


SOURCE=${BASH_SOURCE[0]}

while [ -L "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
    TARGET=$(readlink "$SOURCE")
    if [[ $TARGET == /* ]]; then
        echo "SOURCE '$SOURCE' is an absolute symlink to '$TARGET'"
        SOURCE=$TARGET
    else
        DIR=$( dirname "$SOURCE" )
        echo "SOURCE '$SOURCE' is a relative symlink to '$TARGET' (relative to '$DIR')"
        SOURCE=$DIR/$TARGET # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
    fi
done
# echo "Executing '$SOURCE'"
RDIR=$( dirname "$SOURCE" )
DIR=$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )
if [ "$DIR" != "$RDIR" ]; then
    echo "Directory Path = '$DIR'"
fi

cd $DIR
DIR_ENV="$(ls -a | grep env)"

if [[ -z "$DIR_ENV" ]]; then
    echo "Python virtual environment not exist, create a new one..."
    /usr/bin/python3 -m venv .venv
    DIR_ENV=".venv"
fi

echo "Installing required packages..."
source "$DIR/$DIR_ENV/bin/activate"
pip install -r requirements
echo -e "\r\nPackages installed successfully!"

echo "Finishing setup..."
cat > run.sh <<EOF
#!/usr/bin/env bash


source "$DIR/$DIR_ENV/bin/activate"
python $DIR/main.py
echo -e "\r\nApplication has been stopped.\r\n"
EOF
chmod +x run.sh