# FastDB
A simple client-server relational database management system written in Python using SQLite and socket functionalities.

## Usage

- You need to run the server first by typing in a terminal :
```
python3 server.py --addr=ADDRESS --port=PORT
```

```ADDRESS``` is the IP address of the server host
```PORT```	  is the port to use

- Next, you need to run the client via this command:
```
python3 client.py --addr=ADDRESS --port=PORT --user=USERNAME
```

```ADDRESS```  here is the IP address where the server is running.
```PORT``` 	   the port used by the server.
```USERNAME``` your username on this server. (You must create it first)
