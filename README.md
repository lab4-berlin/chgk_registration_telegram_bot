How to run:


```bash
#Install Python
sudo apt update
sudo apt install python3 python3-pip

#Install dependencies:
pip install python-telegram-bot sqlite3

#Run your bot with:
nohup python bot.py &

#Alternatevely: to keep it running even after disconnecting, use screen or tmux:
screen -S mybot
python bot.py
```
