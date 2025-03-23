"""
__author__: bwandii
__created__: 10/10/2024
__description__: for now, baseline reply bot providing algorithm
                 and data structure interview questions upon interaction.
                 i will scale this to include more functionality
                 as i familiarize myself with discord.py API
"""

import discord
from discord.ext import commands
import json
import random
# you will need your own bot token
from sierra_token import get_token

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

QUESTION_TOPICS = []

# both updated 2025/03/22
# https://leetcode.com/api/problems/algorithms/
with open("question_bank/leetcode_algorithms_problems.json", "r") as f:
    algo_prob_list = json.load(f)

# https://leetcode.com/api/problems/database/
with open("question_bank/leetcode_database_problems.json", "r") as t:
    db_prob_list = json.load(t)

algo_list = algo_prob_list["stat_status_pairs"]
db_list = db_prob_list["stat_status_pairs"]
# hash map to O(1) retrieve question
db_lookup = {problem["stat"]["frontend_question_id"]: problem for problem in db_list}
algo_lookup = {
    problem["stat"]["frontend_question_id"]: problem for problem in algo_list
}


def get_problem_by_id(lookup_dict: dict, n: int):
    return lookup_dict.get(n, None)


# topics are int values
def fetch_problems(topic: bool):
    # user wants db list
    if topic == 0:
        return db_list
    elif topic == 1:
        return algo_list
    else:
        return -1


def filter_premium(problems):
    free_problems = []
    for p in problems:
        if p["paid_only"] is False:
            free_problems.append(p)

    return free_problems


# later expand this
def filter_difficulty(problems, difficulty):
    filtered = []
    for p in problems:
        if p["difficulty"]["level"] == difficulty:
            filtered.append(p)

    return filtered


def get_embed_color(question_data):
    if question_data["difficulty"]["level"] == 3:
        embed_color = discord.Color.red()
    elif question_data["difficulty"]["level"] == 2:
        embed_color = discord.Color.orange()
    else:
        embed_color = discord.Color.green()

    return embed_color


def format_difficulty(difficulty):
    if difficulty["level"] == 3:
        return "hard"
    elif difficulty["level"] == 2:
        return "medium"
    else:
        return "easy"


@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)


@bot.tree.command(name="get_random_leetcode")
async def random_leetcode(
    interaction: discord.Interaction,
    include_premium: bool,
    problem_set: bool,
    difficulty_level: int = 0,
):
    # grab random q from my local folder
    try:
        problems = fetch_problems(problem_set)
        if problem_set == 0:
            embed_string = "Database Problem Set"
        elif problem_set == 1:
            embed_string = "Algorithms Problem Set"
        # if user says no premium, filter only free questions for that user.
        if include_premium is False:
            problems = filter_premium(problems)

        if difficulty_level != 0:
            problems = filter_difficulty(problems, difficulty_level)

        random_problem = random.choice(problems)
        title = random_problem["stat"]["question__title"]
        difficulty = random_problem["difficulty"]
        slug = random_problem["stat"]["question__title_slug"]

        difficulty_formatted = format_difficulty(difficulty)

        problem_url = f"https://leetcode.com/problems/{slug}"

        embed_color = get_embed_color(random_problem)

        embed = discord.Embed(title=title, url=problem_url, color=embed_color)
        embed.add_field(name="Problem Set: ", value=embed_string, inline=False)
        embed.add_field(name="Difficulty: ", value=difficulty_formatted, inline=False)

        await interaction.response.send_message(embed=embed)

    except Exception as e:
        await interaction.response.send_message(f"an error occurred: {str(e)}")


# Algo prob set is 1 db prob set is 0
@bot.tree.command(name="get_question_by_id")
async def get_question(
    interaction: discord.Interaction,
    problem_number: int,
    problem_set: bool,
):
    try:
        # db is 0
        if problem_set == 0:
            embed_string = "Database Problem Set"
            problem = get_problem_by_id(db_lookup, problem_number)
        # default is algo
        else:
            embed_string = "Algorithms Problem Set"
            problem = get_problem_by_id(algo_lookup, problem_number)

        title = problem["stat"]["question__title"]
        difficulty = problem["difficulty"]
        slug = problem["stat"]["question__title_slug"]

        difficulty_formatted = format_difficulty(difficulty)

        problem_url = f"https://leetcode.com/problems/{slug}"
        embed_color = get_embed_color(problem)

        embed = discord.Embed(title=title, url=problem_url, color=embed_color)
        embed.add_field(name="Problem Set: ", value=embed_string, inline=False)
        embed.add_field(name="Difficulty: ", value=difficulty_formatted, inline=False)

        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"an error occurred: {str(e)}")


bot.run(get_token())
