'''
    __author__: bwandii
    __created__: 10/10/2024
    __description__: for now, baseline reply bot providing algorithm and data structure interview questions upon interaction.
                     i will scale this to include more functionality as i familiarize myself with discord.py API  
'''
import discord
from discord.ext import commands
import json
import random
from sierra_token import get_token

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

# load question from bank. bank is from leetcode's json https://leetcode.com/api/problems/algorithms/
with open('question_bank/leetcode_problems.json', 'r') as f:
    leetcode_data = json.load(f)
   
   
def fetch_problems():
    return leetcode_data['stat_status_pairs'] 
 
 
def get_embed_color(question_data):
    if question_data['difficulty']['level'] == '3':
        embed_color = discord.Color.red()
    elif question_data['difficulty']['level'] == '2':
        embed_color = discord.Color.orange()
    else:
        embed_color = discord.Color.green()

    return embed_color

        
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)


@bot.tree.command(name="leetcode")
async def leetcode(interaction: discord.Interaction):
    # grab random q from my local folder
    try:
        problems = fetch_problems() 
        random_problem = random.choice(problems)
        title = random_problem['stat']['question__title']
        difficulty = random_problem['difficulty']
        slug =  random_problem['stat']['question__title_slug']

        problem_url = f"https://leetcode.com/problems/{slug}"

        embed_color = get_embed_color(random_problem)        


        embed = discord.Embed(
            title=title,
            url=problem_url,
            color=embed_color
        )
        embed.add_field(name="difficulty", value=difficulty, inline=False)

        
        await interaction.response.send_message(embed=embed)
    
    except Exception as e:
        await interaction.response.send_message(f"an error occurred: {str(e)}")


bot.run(get_token())