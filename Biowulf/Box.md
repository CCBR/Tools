## Setting up Box on helix:

**Step 1.** _ssh_ into helix and `module load rclone/1.53.1`   

**Step 2**. Follow the instructions listed here until step **7.**: https://www.sussex.ac.uk/its/help/guide.php?id=245

**Step 3.** Once you get step **7.** in the guide above (where it mentions _Remote config_), please answer `n` and follow the instructions listed here: https://rclone.org/remote_setup/

**Step 4.** Open a new terminal (and keep your shell open on helix, you will need this later). From your local machine, you will need to install rclone.
If you have _brew_ installed on your local machine, you can simply run:
```
brew install rclone
```

**Step 5.** Please ensure you are connected to VPN. If you are not, please connect now! Once rclone has finished installing on your local computer, please run:
```
rclone authorize "box"
```

If your browser doesn't open automatically go to the following link: http://127.0.0.1:53682/auth

**Step 6.** You maybe asked to login into Box. In your local terminal, there will be a json string, you want to copy the entire json string:  

> _**Paste the following into your remote machine --->**_
```
{"access_token":"XYZ","token_type":"bearer","refresh_token":"XYZ","expiry":"XYZ"}
```
> _**<---End paste**_

**Step 7.** Copy everything between the bold, italicized print above, and then _paste it into your terminal on helix_, and then enter `y`

That's it! Everything should be setup!

rlcone is a module on Biowulf but just make sure to use the latest version of it (the default module is kind of old). I always use `rclone/1.53.1`. Once it is setup, you can access Box from helix/biowulf from the command line. rclone is really nice and has great documentation! It has a ton of functionality that I haven't explored.

And then you can check how much space you have available or free by running this command:
```
$ rclone about Box:/
Total:   909.495T
Used:    63.867G
Free:    909.432T
```

Or list all your files:
```
$ rclone ls Box:/
```

