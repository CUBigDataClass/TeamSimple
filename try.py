config = {}
exec(compile(open("config.py", "rb").read(), "config.py", 'exec'), config)
#execfile("config.py", config)
print(config["access_key"], config["access_secret"], config["consumer_key"], config["consumer_secret"])
