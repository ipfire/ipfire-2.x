# Setup for /bin/ls to support color, the alias is in /etc/bashrc.
if [ -f "/etc/dircolors" ] ; then
        eval $(dircolors -b /etc/dircolors)

        if [ -f "$HOME/.dircolors" ] ; then
                eval $(dircolors -b $HOME/.dircolors)
        fi
fi
alias ls='ls --color=auto'
