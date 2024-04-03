
Optional Helpers for Drink
==========================

Those are all for zsh. If some kind user of oh-my-zsh wants to make a module
out of these, that would be very much appreciated.

Porting the command completion and drinkrefresh to bash would be awesome too.


_drink
------

Command completion for zsh. Very much recommended. Drop this into your $fpath.

drinkrefresh
------------

Both, a user command and a precmd hook. Provides needed setup for keeping
prompt info up to date and make change detection work.

When run with no arguments (as you use it for the precmd hook), nothing is
printed. Just some internal variables are updated.

When run with `-r`, it will cause zsh to be re-executed if the drink repository
and current zsh session are out of sync.

When `-v` is added, it will print a bit of information about the internal
state. In combination with `-r`, it will also print a summary of changes in the
drink recpository since the last shell startup.

**Installation**: Copy the drinkrefresh file into a directory in your fpath and
put the following into your `.zshrc`:

    whence drink >/dev/null && {
        # drinkrefresh will reference DRINKDIR as ~drink
        hash -d drink="$HOME/$(source ~/.drinkrc; echo $DRINKDIR)"
        # Exported for e. g. starship
        export drink_prompt_info
        # Register this also as a precmd:
        add-zsh-hook precmd drinkrefresh
        drinkrefresh
        # Set drink_headref once as the baseline for this shell session.
        drink_headref=$drink_current_headref
    }


zshaliases
----------

Handy shortcuts for common commands.
