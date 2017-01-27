# ipfire-2.x

Cross Compiling for ARM (From Ubuntu 16.04)
# http://forum.ipfire.org/viewtopic.php?t=10811

sudo apt-get install qemu-user-static

sudo ./make.sh clean
sudo ./make.sh --target=armv5tel gettoolchain
sudo ./make.sh --target=armv5tel downloadsrc
sudo ./make.sh --target=armv5tel build BUILD_IMAGES=1

Wait for a few DAYS!

In case you get postfix errors, SKIP adding the postfix package 
