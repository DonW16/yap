import discord
from discord import app_commands
from collections import Counter
import datetime
import sqlite3
import random
import os
import pytz
import asyncio

intents = discord.Intents.default()
intents.message_content = True  # Enable the message content intent
intents.typing = False
intents.presences = False

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    await tree.sync()
    print(f'Logged in as {client.user.name}')

async def analyze(interaction: discord.Interaction):
    await interaction.response.defer()  # Acknowledge the interaction to avoid timeout
    # Get all the messages within the time window
    current_datetime = datetime.datetime.now()
    start_time = datetime.datetime(current_datetime.year, current_datetime.month, current_datetime.day, 0, 0, 0)
    end_time = datetime.datetime(current_datetime.year, current_datetime.month, current_datetime.day, 23, 59, 59)
    channel = interaction.channel
    messages = []
    async for message in channel.history(limit=None):
        messages.append(message)
    
    # Get the timezone from the first message
    first_message = await anext(channel.history(limit=1), None)
    if first_message:
        timezone = first_message.created_at.tzinfo
    else:
        timezone = datetime.timezone.utc  # Default to UTC if no messages are found
    
    # Convert start_time and end_time to offset-aware datetimes
    start_time = start_time.replace(tzinfo=timezone)
    end_time = end_time.replace(tzinfo=timezone)
    
    messages_within_time_window = [message for message in messages if start_time <= message.created_at <= end_time]

    # Count the number of messages per user
    user_message_count = Counter(message.author for message in messages_within_time_window)

    # Get the top 3 most active posters
    top_posters = user_message_count.most_common(3)

    # Rank the top posters
    ranked_posters = {user: rank for rank, (user, _) in enumerate(top_posters, 1)}

    # Count the total number of messages
    total_messages_today = len(messages_within_time_window)

    # Count the total number of words
    total_words_today = sum(len(message.content.split()) for message in messages_within_time_window)

    # Count the most commonly used word
    word_count = Counter(word for message in messages_within_time_window for word in message.content.split())
    most_common_word_today = word_count.most_common(1)[0][0]

    # Find the longest message
    longest_message = max(messages_within_time_window, key=lambda message: len(message.content))

    # Longest message url
    longest_message_url_today = longest_message.jump_url

    # Longest message author
    longest_message_author_today = longest_message.author.global_name

    # Longest message author profile
    longest_message_author_profile = longest_message.author.avatar.url

    # Get the length of the longest message
    longest_message_length_today = len(longest_message.content)

    # Get the topic of discussion
    topic_of_discussion = "Your topic of discussion here"

    # Create the report
    current_datetime = datetime.datetime.now()
    
    current_datetime = current_datetime.strftime('%d-%m-%Y %H:%M:%S')
    emojis = ["🥇", "🥈", "🥉"]
    
    report = f'**Top 3 Most Active Yappers for today:** \n'
    report += f"\n**Total Number of Messages today:** {total_messages_today}\n"
    report += f"**Total Number of Words today:** {total_words_today}\n"
    report += f"**Most Commonly Used Word today:** {most_common_word_today}\n"
    report += f"**Longest Message today:** {longest_message_length_today} characters by {longest_message_author_today} {longest_message_url_today} \n"
    
    for rank, (user, count) in enumerate(top_posters, 1):
        if rank <= 3:
            emoji = emojis[rank - 1]
        else:
            emoji = random.choice(["🎖️", "🏆", "🎯", "🔥", "⭐", "💯", "🤡"])
        report += f"{rank}. {user.name} - {count} messages {emoji}\n"

    #report += f"**Topic of Discussion:** {topic_of_discussion}\n"
    
    # Define adapter and converter functions
    def adapt_datetime(dt):
        return dt.strftime('%Y-%m-%d %H:%M:%S')

    def convert_datetime(s):
        return datetime.datetime.strptime(s.decode('utf-8'), '%d-%m-%Y %H:%M:%S')

    # Register the adapter and converter
    sqlite3.register_adapter(datetime.datetime, adapt_datetime)
    sqlite3.register_converter('DATETIME', convert_datetime)

    # Connect to the database with the new converter
    conn = sqlite3.connect('yap.db')
    cursor = conn.cursor()

    # Create table to store the creation date of the database
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS database_creation_date (
            created_at DATETIME
        )
    ''')

    # Database creation date
    database_creation_time = datetime.datetime.now()

    # Insert the creation date of the database if it doesn't exist
    cursor.execute('''
        INSERT OR IGNORE INTO database_creation_date (created_at)
        VALUES (?)
    ''', (database_creation_time,))

    # Get the creation date of the database
    cursor.execute('''
        SELECT created_at FROM database_creation_date
    ''')

    # Get the creation date of the database
    created_at = cursor.fetchone()

    # Update the message count for each user
    for user, new_count in user_message_count.items():
        cursor.execute('''
            SELECT message_count FROM message_counts WHERE user_id = ?
        ''', (user.id,))
        result = cursor.fetchone()
        
        if result:
            current_count = result[0]
            if new_count != current_count:
                difference = new_count - current_count
                cursor.execute('''
                    UPDATE message_counts
                    SET message_count = message_count + ?
                    WHERE user_id = ?
                ''', (difference, user.id))
        else:
            print()
            cursor.execute('''
                INSERT INTO message_counts (user_id, username, message_count)
                VALUES (?, ?, ?)
            ''', (user.id, user.name, new_count))

    # Get the leaderboard of top 10 posters
    cursor.execute('''
        SELECT username, message_count
        FROM message_counts
        ORDER BY message_count DESC
        LIMIT 10
    ''')

    top_posters = cursor.fetchall()

    created_at = created_at[0]

    if created_at:
        # Add the leaderboard to the report
        report += f'\n**Yappers Leaderboard started on: {created_at}**\n'
        emojis = ["🥇", "🥈", "🥉"]
        for rank, (username, message_count) in enumerate(top_posters, 1):
            if rank <= 3:
                emoji = emojis[rank - 1]
            else:
                emoji = random.choice(["🎖️", "🏆", "🎯", "🔥", "⭐", "💯" "🤡"])
            report += f'{rank}. {username} - {message_count} messages {emoji} \n'
    else:
        #report += f"\n**Database Created At:** No data"
        report += f'\n**Yappers Leaderboard: ** No data\n'
        for rank, (username, message_count) in enumerate(top_posters, 1):
            report += f'{rank}. {username} - {message_count} messages\n'

    # Count the most commonly used words all time
    all_time_word_count = Counter(word for message in messages for word in message.content.split())
    most_common_words_all_time = all_time_word_count.most_common(10)

    # Create the leaderboard for most commonly used words
    word_leaderboard = ""
    
    for rank, (word, count) in enumerate(most_common_words_all_time, 1):
        word_leaderboard += f"{rank}. {word} - {count} occurrences\n"
    report += f"\n**Most Commonly Used Words all time:**\n{word_leaderboard}"

    conn.commit()
    conn.close()

    # Send the report as a rich embed
    embed = discord.Embed(title=f"Iron Edge Yapping Report: {current_datetime}", description=report, color=discord.Color.blue())
    await interaction.followup.send(embed=embed)

@tree.command(name="report", description="Generate a report of the channel's yapping activity")
async def report(interaction: discord.Interaction):
    await analyze(interaction)
    await tree.sync()

async def run_report_at_midnight():
    # Your implementation here
    pass

async def main():
    # Schedule the task
    task = asyncio.create_task(run_report_at_midnight())
    # Optionally, await the task if you want to wait for its completion
    await task

if __name__ == "__main__":
    # Run the main coroutine, which will start the event loop
    asyncio.run(main())

    # Fetch discord token via os.env
    token = os.getenv('DISCORD_TOKEN')

    # Run the client with the token
    client.run(token)