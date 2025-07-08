# Discord Ticket & Interview Bot - Modular Structure

This bot provides an advanced ticket system, interview (application) system, and moderation tools for Discord servers. It is designed in a modular structure and can be easily extended.

## Features

### 🎫 Ticket System
- Modal-based ticket creation
- Role management with penalty menu
- Save ticket transcript
- Automatic channel management

### 📝 Interview (Application) System
- Start interview with slash command (`/interview`)
- 20 Hard RP questions, answered in 4 pages via modal
- Answers are sent as an embed to the log channel for review
- Answers are archived as JSON (only in file, not sent to channel)
- When the interview is completed, the user is given a "waiting for approval" role and their old role is removed
- Only users with a specific role can start the interview

### ✅ Interview Approval Command
- Admins can give the IC-NAME role to a user and remove the waiting role with `/interviewapprove <user_id>`
- The result is logged both in the terminal and the log channel
- Unauthorized usage, user not found, and role operations are also logged

### 🛡️ Moderation Commands
- User registration system
- Role management (register, female, male, name)
- Message clearing (clear)
- Channel deletion (deletechannel)
- View avatar

### 🌐 Server Management
- Server status notifications (active, restart, maintenance)
- IP address sharing
- Voice channel management

### 👥 Member Management
- Automatic role assignment
- Join/leave logs
- Registration system

## Installation

1. **Install requirements:**
```bash
pip install -r requirements.txt
```

2. **Edit the config file:**
Update the settings in `config.json` according to your server.

3. **Run the bot:**
```bash
python bot.py
```

## Folder Structure

```
ticket-bot/
├── bot.py                 # Main bot file
├── config.json            # Configuration file
├── requirements.txt       # Required libraries
├── README.md              # This file
├── cogs/                  # Command modules
│   ├── __init__.py
│   ├── ticket_system.py   # Ticket system commands
│   ├── server_commands.py # Server commands
│   ├── moderation_commands.py # Moderation commands
│   └── interview_system.py    # Interview system and approval command
├── events/                # Event modules
│   ├── __init__.py
│   ├── ready.py           # When the bot is ready
│   └── member_events.py   # Member events
├── utils/                 # Helper functions
│   ├── __init__.py
│   └── helpers.py         # General helper functions
└── data/                  # Ticket data
    └── *.json
└── responses/             # Interview answers (JSON archive)
    └── *_interview_final.json
```

## Commands

### Ticket Commands
- `/ticket` - Creates the ticket system embed
- `/dataticket <user_id>` - Retrieves the user's ticket transcript

### Interview Commands
- `/interview` - Starts the interview (application) system (only for users with a specific role)
- `/interviewapprove <user_id>` - Gives the IC-NAME role to the user and removes the waiting role (admin only)

### Server Commands
- `/active` - Announces server active status
- `/restart` - Announces server restart status
- `/maintenance` - Announces server maintenance status
- `/ip` - Shows the server IP address

### Moderation Commands
- `/register <user>` - Registers the user
- `/female <user>` - Gives the female role to the user
- `/male <user>` - Gives the male role to the user
- `/name <user> <new_name>` - Changes the user's name
- `/avatar <user>` - Shows the user's avatar
- `/clear <amount>` - Deletes the specified number of messages
- `/deletechannel <channel_name>` - Deletes the channel with the specified name
- `/join` - Joins the voice channel
- `/leave` - Leaves the voice channel

## Config Settings

You can configure the following settings in `config.json`:

- **Token**: Discord bot token
- **Prefix**: Command prefix
- **Role IDs**: Admin, moderator, ticket user roles, IC-NAME role, interview waiting role
- **Channel IDs**: Log, join, leave, register, interview log channel
- **Embed settings**: Color, title, description
- **Penalty roles**: Warning, CK point, blacklist roles
- **Server info**: IP, Discord URL, images
- **Interview questions**: `interview_questions` list (20 items)
- **Interview log channel**: `interview_channel_id` (channel where answers are sent as embed)
- **Interview waiting role**: `interview_role_to_add` (role to be given after interview)
- **IC-NAME role**: Role to be given with `/interviewapprove` (fixed: 1330578864396828682)

## Logging

- All operations performed with the `/interviewapprove` command are logged both in the terminal and in the log channel with ID `1391725335263051806`.
- Success, error, unauthorized usage, and user not found situations are logged.

## Development

### Adding a New Command
1. Create a new file in the `cogs/` folder
2. Inherit from the `commands.Cog` class
3. Add a `setup()` function
4. The bot will automatically load it

### Adding a New Event
1. Create a new file in the `events/` folder
2. Inherit from the `commands.Cog` class
3. Use the `@commands.Cog.listener()` decorator
4. Add a `setup()` function

## License

This project is licensed under the MIT license.

## Support

If you have any issues, please open an issue or contact us. 