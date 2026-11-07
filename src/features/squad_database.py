"""
Comprehensive European Squads & Active Rosters Database (2024/2025/2026 Season).
Covers major and mid-table clubs across Premier League, La Liga, Serie A, Bundesliga, and Ligue 1.
Includes positions, Player Impact Scores (PIS), goal contributions, and defensive impacts.
"""
from typing import Dict, List, Any

# Map dataset team names to canonical squad names
CLUB_ALIASES: Dict[str, str] = {
    "Bayern München": "Bayern Munich",
    "Bayern Munchen": "Bayern Munich",
    "Borussia Mönchengladbach": "Borussia Monchengladbach",
    "Mönchengladbach": "Borussia Monchengladbach",
    "Ath Madrid": "Atletico Madrid",
    "Ath Bilbao": "Athletic Bilbao",
    "Sociedad": "Real Sociedad",
    "Betis": "Real Betis",
    "Vallecano": "Rayo Vallecano",
    "Espanol": "Espanyol",
    "Dortmund": "Borussia Dortmund",
    "Leverkusen": "Bayer Leverkusen",
    "M'gladbach": "Borussia Monchengladbach",
    "Ein Frankfurt": "Eintracht Frankfurt",
    "Wolverhampton": "Wolves",
    "Man City": "Manchester City",
    "Man United": "Manchester United",
    "Paris SG": "Paris Saint-Germain"
}

EXPANDED_SQUAD_DATABASE: Dict[str, Dict[str, Dict[str, Any]]] = {
    # ==================== PREMIER LEAGUE ====================
    "Manchester City": {
        "Erling Haaland": {"pos": "FWD", "role": "Striker", "pis": 9.8, "goal_share": 0.36, "def_impact": 0.00, "is_gk": False},
        "Rodri": {"pos": "MID", "role": "Defensive Midfield", "pis": 9.6, "goal_share": 0.08, "def_impact": 0.28, "is_gk": False},
        "Kevin De Bruyne": {"pos": "MID", "role": "Attacking Midfield", "pis": 9.4, "goal_share": 0.12, "def_impact": 0.03, "is_gk": False},
        "Phil Foden": {"pos": "FWD", "role": "Winger / Playmaker", "pis": 9.0, "goal_share": 0.22, "def_impact": 0.04, "is_gk": False},
        "Bernardo Silva": {"pos": "MID", "role": "Central Midfield", "pis": 8.8, "goal_share": 0.10, "def_impact": 0.12, "is_gk": False},
        "Ruben Dias": {"pos": "DEF", "role": "Centre Back", "pis": 8.9, "goal_share": 0.02, "def_impact": 0.20, "is_gk": False},
        "Josko Gvardiol": {"pos": "DEF", "role": "Left Back / CB", "pis": 8.6, "goal_share": 0.08, "def_impact": 0.14, "is_gk": False},
        "Manuel Akanji": {"pos": "DEF", "role": "Centre Back", "pis": 8.3, "goal_share": 0.03, "def_impact": 0.15, "is_gk": False},
        "Ederson": {"pos": "GK", "role": "Goalkeeper", "pis": 8.8, "goal_share": 0.00, "def_impact": 0.18, "is_gk": True},
        "Stefan Ortega": {"pos": "GK", "role": "Backup Goalkeeper", "pis": 7.8, "goal_share": 0.00, "def_impact": 0.10, "is_gk": True},
        "Jeremy Doku": {"pos": "FWD", "role": "Winger", "pis": 8.3, "goal_share": 0.10, "def_impact": 0.02, "is_gk": False},
        "Jack Grealish": {"pos": "FWD", "role": "Winger", "pis": 8.2, "goal_share": 0.08, "def_impact": 0.05, "is_gk": False},
        "Mateo Kovacic": {"pos": "MID", "role": "Central Midfield", "pis": 8.1, "goal_share": 0.06, "def_impact": 0.14, "is_gk": False},
        "Ilkay Gundogan": {"pos": "MID", "role": "Central Midfield", "pis": 8.4, "goal_share": 0.12, "def_impact": 0.10, "is_gk": False},
        "Kyle Walker": {"pos": "DEF", "role": "Right Back", "pis": 8.2, "goal_share": 0.01, "def_impact": 0.14, "is_gk": False},
        "John Stones": {"pos": "DEF", "role": "Centre Back / DM", "pis": 8.5, "goal_share": 0.04, "def_impact": 0.16, "is_gk": False},
        "Nathan Ake": {"pos": "DEF", "role": "Centre Back / LB", "pis": 8.2, "goal_share": 0.03, "def_impact": 0.15, "is_gk": False},
        "Savinho": {"pos": "FWD", "role": "Winger", "pis": 8.1, "goal_share": 0.10, "def_impact": 0.02, "is_gk": False},
        "Rico Lewis": {"pos": "DEF", "role": "Fullback / Midfield", "pis": 7.9, "goal_share": 0.04, "def_impact": 0.10, "is_gk": False}
    },
    "Arsenal": {
        "Bukayo Saka": {"pos": "FWD", "role": "Right Winger", "pis": 9.6, "goal_share": 0.26, "def_impact": 0.05, "is_gk": False},
        "Martin Odegaard": {"pos": "MID", "role": "Attacking Midfield", "pis": 9.3, "goal_share": 0.18, "def_impact": 0.06, "is_gk": False},
        "Declan Rice": {"pos": "MID", "role": "Central Midfield / DM", "pis": 9.2, "goal_share": 0.10, "def_impact": 0.24, "is_gk": False},
        "William Saliba": {"pos": "DEF", "role": "Centre Back", "pis": 9.3, "goal_share": 0.02, "def_impact": 0.24, "is_gk": False},
        "Gabriel Magalhaes": {"pos": "DEF", "role": "Centre Back", "pis": 9.0, "goal_share": 0.06, "def_impact": 0.20, "is_gk": False},
        "Kai Havertz": {"pos": "FWD", "role": "Forward / Striker", "pis": 8.7, "goal_share": 0.20, "def_impact": 0.06, "is_gk": False},
        "David Raya": {"pos": "GK", "role": "Goalkeeper", "pis": 8.9, "goal_share": 0.00, "def_impact": 0.20, "is_gk": True},
        "Neto": {"pos": "GK", "role": "Backup Goalkeeper", "pis": 7.6, "goal_share": 0.00, "def_impact": 0.08, "is_gk": True},
        "Gabriel Martinelli": {"pos": "FWD", "role": "Left Winger", "pis": 8.5, "goal_share": 0.14, "def_impact": 0.04, "is_gk": False},
        "Leandro Trossard": {"pos": "FWD", "role": "Forward / Winger", "pis": 8.4, "goal_share": 0.15, "def_impact": 0.03, "is_gk": False},
        "Riccardo Calafiori": {"pos": "DEF", "role": "Left Back / CB", "pis": 8.4, "goal_share": 0.04, "def_impact": 0.14, "is_gk": False},
        "Jurrien Timber": {"pos": "DEF", "role": "Fullback", "pis": 8.3, "goal_share": 0.03, "def_impact": 0.12, "is_gk": False},
        "Ben White": {"pos": "DEF", "role": "Right Back", "pis": 8.4, "goal_share": 0.03, "def_impact": 0.15, "is_gk": False},
        "Mikel Merino": {"pos": "MID", "role": "Central Midfield", "pis": 8.2, "goal_share": 0.08, "def_impact": 0.14, "is_gk": False},
        "Thomas Partey": {"pos": "MID", "role": "Defensive Midfield", "pis": 8.2, "goal_share": 0.04, "def_impact": 0.16, "is_gk": False},
        "Jorginho": {"pos": "MID", "role": "Deep-lying Midfield", "pis": 7.9, "goal_share": 0.02, "def_impact": 0.10, "is_gk": False},
        "Raheem Sterling": {"pos": "FWD", "role": "Winger", "pis": 8.0, "goal_share": 0.08, "def_impact": 0.02, "is_gk": False},
        "Oleksandr Zinchenko": {"pos": "DEF", "role": "Left Back", "pis": 7.9, "goal_share": 0.02, "def_impact": 0.08, "is_gk": False}
    },
    "Liverpool": {
        "Mohamed Salah": {"pos": "FWD", "role": "Right Winger / Striker", "pis": 9.7, "goal_share": 0.34, "def_impact": 0.02, "is_gk": False},
        "Virgil van Dijk": {"pos": "DEF", "role": "Centre Back (Captain)", "pis": 9.5, "goal_share": 0.05, "def_impact": 0.25, "is_gk": False},
        "Alisson": {"pos": "GK", "role": "Goalkeeper", "pis": 9.2, "goal_share": 0.00, "def_impact": 0.22, "is_gk": True},
        "Caoimhin Kelleher": {"pos": "GK", "role": "Backup Goalkeeper", "pis": 8.3, "goal_share": 0.00, "def_impact": 0.12, "is_gk": True},
        "Trent Alexander-Arnold": {"pos": "DEF", "role": "Right Back / Playmaker", "pis": 9.3, "goal_share": 0.08, "def_impact": 0.10, "is_gk": False},
        "Alexis Mac Allister": {"pos": "MID", "role": "Central Midfield", "pis": 8.8, "goal_share": 0.10, "def_impact": 0.15, "is_gk": False},
        "Ryan Gravenberch": {"pos": "MID", "role": "Defensive Midfield", "pis": 8.7, "goal_share": 0.06, "def_impact": 0.18, "is_gk": False},
        "Luis Diaz": {"pos": "FWD", "role": "Left Winger", "pis": 8.9, "goal_share": 0.18, "def_impact": 0.04, "is_gk": False},
        "Dominik Szoboszlai": {"pos": "MID", "role": "Attacking Midfield", "pis": 8.6, "goal_share": 0.12, "def_impact": 0.08, "is_gk": False},
        "Darwin Nunez": {"pos": "FWD", "role": "Striker", "pis": 8.4, "goal_share": 0.16, "def_impact": 0.02, "is_gk": False},
        "Cody Gakpo": {"pos": "FWD", "role": "Forward / Winger", "pis": 8.5, "goal_share": 0.15, "def_impact": 0.03, "is_gk": False},
        "Ibrahima Konate": {"pos": "DEF", "role": "Centre Back", "pis": 8.6, "goal_share": 0.02, "def_impact": 0.18, "is_gk": False},
        "Andrew Robertson": {"pos": "DEF", "role": "Left Back", "pis": 8.4, "goal_share": 0.02, "def_impact": 0.14, "is_gk": False},
        "Curtis Jones": {"pos": "MID", "role": "Central Midfield", "pis": 8.1, "goal_share": 0.06, "def_impact": 0.10, "is_gk": False},
        "Harvey Elliott": {"pos": "MID", "role": "Attacking Midfield", "pis": 8.0, "goal_share": 0.08, "def_impact": 0.04, "is_gk": False},
        "Kostas Tsimikas": {"pos": "DEF", "role": "Left Back", "pis": 7.8, "goal_share": 0.01, "def_impact": 0.09, "is_gk": False},
        "Federico Chiesa": {"pos": "FWD", "role": "Winger", "pis": 8.1, "goal_share": 0.10, "def_impact": 0.02, "is_gk": False}
    },
    "Chelsea": {
        "Cole Palmer": {"pos": "FWD", "role": "Attacking Midfielder / Winger", "pis": 9.5, "goal_share": 0.35, "def_impact": 0.03, "is_gk": False},
        "Nicolas Jackson": {"pos": "FWD", "role": "Striker", "pis": 8.4, "goal_share": 0.22, "def_impact": 0.03, "is_gk": False},
        "Moises Caicedo": {"pos": "MID", "role": "Defensive Midfield", "pis": 8.8, "goal_share": 0.04, "def_impact": 0.22, "is_gk": False},
        "Enzo Fernandez": {"pos": "MID", "role": "Central Midfield", "pis": 8.4, "goal_share": 0.08, "def_impact": 0.10, "is_gk": False},
        "Levi Colwill": {"pos": "DEF", "role": "Centre Back", "pis": 8.3, "goal_share": 0.02, "def_impact": 0.16, "is_gk": False},
        "Wesley Fofana": {"pos": "DEF", "role": "Centre Back", "pis": 8.2, "goal_share": 0.01, "def_impact": 0.15, "is_gk": False},
        "Robert Sanchez": {"pos": "GK", "role": "Goalkeeper", "pis": 8.0, "goal_share": 0.00, "def_impact": 0.14, "is_gk": True},
        "Filip Jorgensen": {"pos": "GK", "role": "Backup Goalkeeper", "pis": 7.6, "goal_share": 0.00, "def_impact": 0.08, "is_gk": True},
        "Noni Madueke": {"pos": "FWD", "role": "Right Winger", "pis": 8.2, "goal_share": 0.14, "def_impact": 0.02, "is_gk": False},
        "Pedro Neto": {"pos": "FWD", "role": "Winger", "pis": 8.3, "goal_share": 0.12, "def_impact": 0.03, "is_gk": False},
        "Marc Cucurella": {"pos": "DEF", "role": "Left Back", "pis": 8.2, "goal_share": 0.02, "def_impact": 0.14, "is_gk": False},
        "Malo Gusto": {"pos": "DEF", "role": "Right Back", "pis": 8.1, "goal_share": 0.02, "def_impact": 0.12, "is_gk": False},
        "Christopher Nkunku": {"pos": "FWD", "role": "Forward", "pis": 8.5, "goal_share": 0.18, "def_impact": 0.02, "is_gk": False},
        "Jadon Sancho": {"pos": "FWD", "role": "Winger", "pis": 8.1, "goal_share": 0.08, "def_impact": 0.02, "is_gk": False},
        "Romeo Lavia": {"pos": "MID", "role": "Defensive Midfield", "pis": 8.1, "goal_share": 0.02, "def_impact": 0.15, "is_gk": False},
        "Reece James": {"pos": "DEF", "role": "Right Back (Captain)", "pis": 8.4, "goal_share": 0.04, "def_impact": 0.14, "is_gk": False}
    },
    "Manchester United": {
        "Bruno Fernandes": {"pos": "MID", "role": "Attacking Midfield (Captain)", "pis": 9.2, "goal_share": 0.22, "def_impact": 0.08, "is_gk": False},
        "Marcus Rashford": {"pos": "FWD", "role": "Left Winger / Forward", "pis": 8.4, "goal_share": 0.18, "def_impact": 0.02, "is_gk": False},
        "Kobbie Mainoo": {"pos": "MID", "role": "Central Midfield", "pis": 8.5, "goal_share": 0.08, "def_impact": 0.15, "is_gk": False},
        "Alejandro Garnacho": {"pos": "FWD", "role": "Winger", "pis": 8.4, "goal_share": 0.18, "def_impact": 0.03, "is_gk": False},
        "Rasmus Hojlund": {"pos": "FWD", "role": "Striker", "pis": 8.3, "goal_share": 0.22, "def_impact": 0.02, "is_gk": False},
        "Lisandro Martinez": {"pos": "DEF", "role": "Centre Back", "pis": 8.6, "goal_share": 0.02, "def_impact": 0.22, "is_gk": False},
        "Matthijs de Ligt": {"pos": "DEF", "role": "Centre Back", "pis": 8.5, "goal_share": 0.04, "def_impact": 0.18, "is_gk": False},
        "Andre Onana": {"pos": "GK", "role": "Goalkeeper", "pis": 8.3, "goal_share": 0.00, "def_impact": 0.16, "is_gk": True},
        "Altay Bayindir": {"pos": "GK", "role": "Backup Goalkeeper", "pis": 7.4, "goal_share": 0.00, "def_impact": 0.06, "is_gk": True},
        "Manuel Ugarte": {"pos": "MID", "role": "Defensive Midfield", "pis": 8.2, "goal_share": 0.02, "def_impact": 0.18, "is_gk": False},
        "Noussair Mazraoui": {"pos": "DEF", "role": "Fullback", "pis": 8.1, "goal_share": 0.02, "def_impact": 0.12, "is_gk": False},
        "Diogo Dalot": {"pos": "DEF", "role": "Fullback", "pis": 8.2, "goal_share": 0.04, "def_impact": 0.12, "is_gk": False},
        "Amad Diallo": {"pos": "FWD", "role": "Winger", "pis": 8.0, "goal_share": 0.10, "def_impact": 0.03, "is_gk": False},
        "Joshua Zirkzee": {"pos": "FWD", "role": "Striker", "pis": 8.0, "goal_share": 0.14, "def_impact": 0.03, "is_gk": False},
        "Casemiro": {"pos": "MID", "role": "Defensive Midfield", "pis": 8.0, "goal_share": 0.06, "def_impact": 0.12, "is_gk": False}
    },
    "Tottenham": {
        "Son Heung-min": {"pos": "FWD", "role": "Left Winger / Forward (Captain)", "pis": 9.3, "goal_share": 0.28, "def_impact": 0.02, "is_gk": False},
        "James Maddison": {"pos": "MID", "role": "Attacking Midfield", "pis": 8.8, "goal_share": 0.16, "def_impact": 0.04, "is_gk": False},
        "Dejan Kulusevski": {"pos": "MID", "role": "Winger / Playmaker", "pis": 8.6, "goal_share": 0.14, "def_impact": 0.08, "is_gk": False},
        "Dominic Solanke": {"pos": "FWD", "role": "Striker", "pis": 8.5, "goal_share": 0.24, "def_impact": 0.03, "is_gk": False},
        "Cristian Romero": {"pos": "DEF", "role": "Centre Back", "pis": 8.8, "goal_share": 0.05, "def_impact": 0.22, "is_gk": False},
        "Micky van de Ven": {"pos": "DEF", "role": "Centre Back", "pis": 8.7, "goal_share": 0.04, "def_impact": 0.20, "is_gk": False},
        "Guglielmo Vicario": {"pos": "GK", "role": "Goalkeeper", "pis": 8.4, "goal_share": 0.00, "def_impact": 0.16, "is_gk": True},
        "Pedro Porro": {"pos": "DEF", "role": "Right Wingback", "pis": 8.4, "goal_share": 0.08, "def_impact": 0.10, "is_gk": False},
        "Destiny Udogie": {"pos": "DEF", "role": "Left Wingback", "pis": 8.3, "goal_share": 0.04, "def_impact": 0.12, "is_gk": False},
        "Pape Matar Sarr": {"pos": "MID", "role": "Central Midfield", "pis": 8.1, "goal_share": 0.06, "def_impact": 0.12, "is_gk": False},
        "Yves Bissouma": {"pos": "MID", "role": "Defensive Midfield", "pis": 8.1, "goal_share": 0.04, "def_impact": 0.16, "is_gk": False},
        "Brennan Johnson": {"pos": "FWD", "role": "Winger", "pis": 8.3, "goal_share": 0.18, "def_impact": 0.02, "is_gk": False},
        "Richarlison": {"pos": "FWD", "role": "Forward", "pis": 8.1, "goal_share": 0.14, "def_impact": 0.02, "is_gk": False}
    },
    "Aston Villa": {
        "Ollie Watkins": {"pos": "FWD", "role": "Striker", "pis": 9.2, "goal_share": 0.32, "def_impact": 0.03, "is_gk": False},
        "Emiliano Martinez": {"pos": "GK", "role": "Goalkeeper (World Cup Winner)", "pis": 9.0, "goal_share": 0.00, "def_impact": 0.22, "is_gk": True},
        "Morgan Rogers": {"pos": "MID", "role": "Attacking Midfield", "pis": 8.5, "goal_share": 0.16, "def_impact": 0.06, "is_gk": False},
        "Youri Tielemans": {"pos": "MID", "role": "Central Midfield", "pis": 8.4, "goal_share": 0.10, "def_impact": 0.12, "is_gk": False},
        "Pau Torres": {"pos": "DEF", "role": "Centre Back", "pis": 8.5, "goal_share": 0.03, "def_impact": 0.18, "is_gk": False},
        "Ezri Konsa": {"pos": "DEF", "role": "Centre Back", "pis": 8.3, "goal_share": 0.02, "def_impact": 0.16, "is_gk": False},
        "John McGinn": {"pos": "MID", "role": "Box-to-box Midfield (Captain)", "pis": 8.4, "goal_share": 0.10, "def_impact": 0.12, "is_gk": False},
        "Leon Bailey": {"pos": "FWD", "role": "Right Winger", "pis": 8.3, "goal_share": 0.16, "def_impact": 0.02, "is_gk": False},
        "Amadou Onana": {"pos": "MID", "role": "Defensive Midfield", "pis": 8.3, "goal_share": 0.06, "def_impact": 0.18, "is_gk": False},
        "Lucas Digne": {"pos": "DEF", "role": "Left Back", "pis": 8.1, "goal_share": 0.03, "def_impact": 0.10, "is_gk": False},
        "Jhon Duran": {"pos": "FWD", "role": "Striker / Super-Sub", "pis": 8.4, "goal_share": 0.20, "def_impact": 0.01, "is_gk": False},
        "Matty Cash": {"pos": "DEF", "role": "Right Back", "pis": 8.0, "goal_share": 0.03, "def_impact": 0.11, "is_gk": False}
    },
    "Newcastle": {
        "Alexander Isak": {"pos": "FWD", "role": "Striker", "pis": 9.3, "goal_share": 0.35, "def_impact": 0.02, "is_gk": False},
        "Anthony Gordon": {"pos": "FWD", "role": "Left Winger", "pis": 8.8, "goal_share": 0.20, "def_impact": 0.05, "is_gk": False},
        "Bruno Guimaraes": {"pos": "MID", "role": "Midfield Maestro (Captain)", "pis": 9.0, "goal_share": 0.10, "def_impact": 0.18, "is_gk": False},
        "Joelinton": {"pos": "MID", "role": "Central Midfield Engine", "pis": 8.4, "goal_share": 0.08, "def_impact": 0.15, "is_gk": False},
        "Sandro Tonali": {"pos": "MID", "role": "Central Midfield", "pis": 8.4, "goal_share": 0.06, "def_impact": 0.14, "is_gk": False},
        "Fabian Schar": {"pos": "DEF", "role": "Centre Back", "pis": 8.3, "goal_share": 0.06, "def_impact": 0.16, "is_gk": False},
        "Dan Burn": {"pos": "DEF", "role": "Centre Back", "pis": 8.0, "goal_share": 0.02, "def_impact": 0.15, "is_gk": False},
        "Nick Pope": {"pos": "GK", "role": "Goalkeeper", "pis": 8.3, "goal_share": 0.00, "def_impact": 0.16, "is_gk": True},
        "Tino Livramento": {"pos": "DEF", "role": "Fullback", "pis": 8.1, "goal_share": 0.02, "def_impact": 0.12, "is_gk": False},
        "Lewis Hall": {"pos": "DEF", "role": "Left Back", "pis": 8.1, "goal_share": 0.02, "def_impact": 0.10, "is_gk": False},
        "Harvey Barnes": {"pos": "FWD", "role": "Left Winger", "pis": 8.2, "goal_share": 0.15, "def_impact": 0.02, "is_gk": False},
        "Jacob Murphy": {"pos": "FWD", "role": "Right Winger", "pis": 7.9, "goal_share": 0.08, "def_impact": 0.04, "is_gk": False}
    },
    "Brighton": {
        "Kaoru Mitoma": {"pos": "FWD", "role": "Left Winger", "pis": 8.7, "goal_share": 0.22, "def_impact": 0.04, "is_gk": False},
        "Danny Welbeck": {"pos": "FWD", "role": "Striker", "pis": 8.5, "goal_share": 0.26, "def_impact": 0.03, "is_gk": False},
        "Joao Pedro": {"pos": "FWD", "role": "Striker / Forward", "pis": 8.6, "goal_share": 0.25, "def_impact": 0.02, "is_gk": False},
        "Yankuba Minteh": {"pos": "FWD", "role": "Right Winger", "pis": 8.2, "goal_share": 0.12, "def_impact": 0.03, "is_gk": False},
        "Lewis Dunk": {"pos": "DEF", "role": "Centre Back (Captain)", "pis": 8.4, "goal_share": 0.04, "def_impact": 0.20, "is_gk": False},
        "Jan Paul van Hecke": {"pos": "DEF", "role": "Centre Back", "pis": 8.2, "goal_share": 0.01, "def_impact": 0.16, "is_gk": False},
        "Bart Verbruggen": {"pos": "GK", "role": "Goalkeeper", "pis": 8.2, "goal_share": 0.00, "def_impact": 0.15, "is_gk": True},
        "Carlos Baleba": {"pos": "MID", "role": "Defensive Midfield", "pis": 8.3, "goal_share": 0.04, "def_impact": 0.18, "is_gk": False},
        "Jack Hinshelwood": {"pos": "MID", "role": "Utility Midfield", "pis": 8.0, "goal_share": 0.06, "def_impact": 0.10, "is_gk": False},
        "Pervis Estupinan": {"pos": "DEF", "role": "Left Back", "pis": 8.2, "goal_share": 0.04, "def_impact": 0.12, "is_gk": False}
    },
    "West Ham": {
        "Jarrod Bowen": {"pos": "FWD", "role": "Right Winger / Striker (Captain)", "pis": 8.9, "goal_share": 0.32, "def_impact": 0.04, "is_gk": False},
        "Mohammed Kudus": {"pos": "FWD", "role": "Winger / Playmaker", "pis": 8.8, "goal_share": 0.24, "def_impact": 0.05, "is_gk": False},
        "Lucas Paqueta": {"pos": "MID", "role": "Attacking Midfield", "pis": 8.7, "goal_share": 0.15, "def_impact": 0.10, "is_gk": False},
        "Tomas Soucek": {"pos": "MID", "role": "Central Midfield", "pis": 8.2, "goal_share": 0.12, "def_impact": 0.14, "is_gk": False},
        "Max Kilman": {"pos": "DEF", "role": "Centre Back", "pis": 8.3, "goal_share": 0.02, "def_impact": 0.18, "is_gk": False},
        "Alphonse Areola": {"pos": "GK", "role": "Goalkeeper", "pis": 8.2, "goal_share": 0.00, "def_impact": 0.16, "is_gk": True},
        "Emerson Palmieri": {"pos": "DEF", "role": "Left Back", "pis": 8.0, "goal_share": 0.02, "def_impact": 0.12, "is_gk": False},
        "Michail Antonio": {"pos": "FWD", "role": "Striker", "pis": 7.9, "goal_share": 0.12, "def_impact": 0.02, "is_gk": False}
    },
    "Leicester": {
        "Jamie Vardy": {"pos": "FWD", "role": "Striker / Legend (Captain)", "pis": 8.8, "goal_share": 0.35, "def_impact": 0.01, "is_gk": False},
        "Facundo Buonanotte": {"pos": "MID", "role": "Attacking Midfield / Playmaker", "pis": 8.6, "goal_share": 0.22, "def_impact": 0.04, "is_gk": False},
        "Stephy Mavididi": {"pos": "FWD", "role": "Left Winger", "pis": 8.4, "goal_share": 0.20, "def_impact": 0.03, "is_gk": False},
        "Wilfred Ndidi": {"pos": "MID", "role": "Central / Defensive Midfield", "pis": 8.4, "goal_share": 0.08, "def_impact": 0.20, "is_gk": False},
        "Harry Winks": {"pos": "MID", "role": "Deep-lying Midfield", "pis": 8.3, "goal_share": 0.04, "def_impact": 0.14, "is_gk": False},
        "Mads Hermansen": {"pos": "GK", "role": "Goalkeeper (Shot Stopper)", "pis": 8.4, "goal_share": 0.00, "def_impact": 0.20, "is_gk": True},
        "Danny Ward": {"pos": "GK", "role": "Backup Goalkeeper", "pis": 7.3, "goal_share": 0.00, "def_impact": 0.08, "is_gk": True},
        "Wout Faes": {"pos": "DEF", "role": "Centre Back", "pis": 8.2, "goal_share": 0.04, "def_impact": 0.18, "is_gk": False},
        "Caleb Okoli": {"pos": "DEF", "role": "Centre Back", "pis": 8.1, "goal_share": 0.02, "def_impact": 0.17, "is_gk": False},
        "Jannik Vestergaard": {"pos": "DEF", "role": "Centre Back", "pis": 8.0, "goal_share": 0.03, "def_impact": 0.15, "is_gk": False},
        "James Justin": {"pos": "DEF", "role": "Fullback", "pis": 8.2, "goal_share": 0.06, "def_impact": 0.12, "is_gk": False},
        "Ricardo Pereira": {"pos": "DEF", "role": "Right Back / Leader", "pis": 8.3, "goal_share": 0.05, "def_impact": 0.14, "is_gk": False},
        "Victor Kristiansen": {"pos": "DEF", "role": "Left Back", "pis": 8.0, "goal_share": 0.02, "def_impact": 0.11, "is_gk": False},
        "Bilal El Khannouss": {"pos": "MID", "role": "Creative Midfielder", "pis": 8.3, "goal_share": 0.12, "def_impact": 0.04, "is_gk": False},
        "Jordan Ayew": {"pos": "FWD", "role": "Forward / Striker", "pis": 8.1, "goal_share": 0.15, "def_impact": 0.04, "is_gk": False},
        "Patson Daka": {"pos": "FWD", "role": "Striker", "pis": 8.0, "goal_share": 0.16, "def_impact": 0.02, "is_gk": False},
        "Bobby De Cordova-Reid": {"pos": "FWD", "role": "Utility Forward", "pis": 8.0, "goal_share": 0.10, "def_impact": 0.06, "is_gk": False},
        "Boubakary Soumare": {"pos": "MID", "role": "Defensive Midfield", "pis": 7.9, "goal_share": 0.02, "def_impact": 0.14, "is_gk": False},
        "Kasey McAteer": {"pos": "FWD", "role": "Winger", "pis": 7.8, "goal_share": 0.08, "def_impact": 0.03, "is_gk": False}
    },

    # ==================== SPANISH LA LIGA ====================
    "Real Madrid": {
        "Kylian Mbappe": {"pos": "FWD", "role": "Striker / Forward", "pis": 9.8, "goal_share": 0.35, "def_impact": 0.01, "is_gk": False},
        "Vinicius Junior": {"pos": "FWD", "role": "Left Winger", "pis": 9.7, "goal_share": 0.28, "def_impact": 0.02, "is_gk": False},
        "Jude Bellingham": {"pos": "MID", "role": "Attacking Midfield", "pis": 9.6, "goal_share": 0.20, "def_impact": 0.12, "is_gk": False},
        "Federico Valverde": {"pos": "MID", "role": "Central Midfield Engine", "pis": 9.3, "goal_share": 0.08, "def_impact": 0.20, "is_gk": False},
        "Rodrygo": {"pos": "FWD", "role": "Right Winger", "pis": 8.9, "goal_share": 0.16, "def_impact": 0.04, "is_gk": False},
        "Antonio Rudiger": {"pos": "DEF", "role": "Centre Back", "pis": 9.1, "goal_share": 0.03, "def_impact": 0.24, "is_gk": False},
        "Thibaut Courtois": {"pos": "GK", "role": "Goalkeeper", "pis": 9.3, "goal_share": 0.00, "def_impact": 0.24, "is_gk": True},
        "Andriy Lunin": {"pos": "GK", "role": "Backup Goalkeeper", "pis": 8.3, "goal_share": 0.00, "def_impact": 0.14, "is_gk": True},
        "Aurelien Tchouameni": {"pos": "MID", "role": "Defensive Midfield / CB", "pis": 8.8, "goal_share": 0.03, "def_impact": 0.22, "is_gk": False},
        "Eduardo Camavinga": {"pos": "MID", "role": "Central Midfield / DM", "pis": 8.7, "goal_share": 0.04, "def_impact": 0.18, "is_gk": False},
        "Luka Modric": {"pos": "MID", "role": "Playmaker (Captain)", "pis": 8.4, "goal_share": 0.04, "def_impact": 0.08, "is_gk": False},
        "Eder Militao": {"pos": "DEF", "role": "Centre Back", "pis": 8.8, "goal_share": 0.02, "def_impact": 0.20, "is_gk": False},
        "Ferland Mendy": {"pos": "DEF", "role": "Left Back", "pis": 8.3, "goal_share": 0.01, "def_impact": 0.16, "is_gk": False},
        "Dani Carvajal": {"pos": "DEF", "role": "Right Back", "pis": 8.7, "goal_share": 0.04, "def_impact": 0.16, "is_gk": False},
        "Lucas Vazquez": {"pos": "DEF", "role": "Right Back / Winger", "pis": 8.1, "goal_share": 0.04, "def_impact": 0.10, "is_gk": False},
        "Brahim Diaz": {"pos": "FWD", "role": "Attacking Midfielder", "pis": 8.3, "goal_share": 0.12, "def_impact": 0.03, "is_gk": False},
        "Endrick": {"pos": "FWD", "role": "Striker", "pis": 8.1, "goal_share": 0.14, "def_impact": 0.01, "is_gk": False}
    },
    "Barcelona": {
        "Robert Lewandowski": {"pos": "FWD", "role": "Striker", "pis": 9.6, "goal_share": 0.38, "def_impact": 0.01, "is_gk": False},
        "Lamine Yamal": {"pos": "FWD", "role": "Right Winger", "pis": 9.5, "goal_share": 0.22, "def_impact": 0.04, "is_gk": False},
        "Raphinha": {"pos": "FWD", "role": "Winger / Attacking Mid", "pis": 9.4, "goal_share": 0.25, "def_impact": 0.06, "is_gk": False},
        "Pedri": {"pos": "MID", "role": "Central Midfield Maestro", "pis": 9.2, "goal_share": 0.08, "def_impact": 0.14, "is_gk": False},
        "Dani Olmo": {"pos": "MID", "role": "Attacking Midfield", "pis": 8.9, "goal_share": 0.18, "def_impact": 0.05, "is_gk": False},
        "Pau Cubarsi": {"pos": "DEF", "role": "Centre Back", "pis": 8.8, "goal_share": 0.01, "def_impact": 0.22, "is_gk": False},
        "Inigo Martinez": {"pos": "DEF", "role": "Centre Back", "pis": 8.5, "goal_share": 0.02, "def_impact": 0.18, "is_gk": False},
        "Jules Kounde": {"pos": "DEF", "role": "Right Back", "pis": 8.9, "goal_share": 0.04, "def_impact": 0.18, "is_gk": False},
        "Alejandro Balde": {"pos": "DEF", "role": "Left Back", "pis": 8.4, "goal_share": 0.02, "def_impact": 0.12, "is_gk": False},
        "Marc Casado": {"pos": "MID", "role": "Defensive Midfield", "pis": 8.5, "goal_share": 0.02, "def_impact": 0.18, "is_gk": False},
        "Inaki Pena": {"pos": "GK", "role": "Goalkeeper", "pis": 8.0, "goal_share": 0.00, "def_impact": 0.14, "is_gk": True},
        "Wojciech Szczesny": {"pos": "GK", "role": "Goalkeeper", "pis": 8.2, "goal_share": 0.00, "def_impact": 0.16, "is_gk": True},
        "Marc-Andre ter Stegen": {"pos": "GK", "role": "Goalkeeper (Captain)", "pis": 8.9, "goal_share": 0.00, "def_impact": 0.20, "is_gk": True},
        "Frenkie de Jong": {"pos": "MID", "role": "Central Midfield", "pis": 8.6, "goal_share": 0.05, "def_impact": 0.12, "is_gk": False},
        "Gavi": {"pos": "MID", "role": "Central Midfield", "pis": 8.6, "goal_share": 0.06, "def_impact": 0.14, "is_gk": False},
        "Ferran Torres": {"pos": "FWD", "role": "Forward", "pis": 8.0, "goal_share": 0.12, "def_impact": 0.02, "is_gk": False}
    },
    "Atletico Madrid": {
        "Antoine Griezmann": {"pos": "FWD", "role": "Forward / Playmaker", "pis": 9.4, "goal_share": 0.28, "def_impact": 0.08, "is_gk": False},
        "Julian Alvarez": {"pos": "FWD", "role": "Striker / Forward", "pis": 9.1, "goal_share": 0.26, "def_impact": 0.04, "is_gk": False},
        "Alexander Sorloth": {"pos": "FWD", "role": "Striker", "pis": 8.5, "goal_share": 0.22, "def_impact": 0.02, "is_gk": False},
        "Jan Oblak": {"pos": "GK", "role": "Goalkeeper", "pis": 9.0, "goal_share": 0.00, "def_impact": 0.22, "is_gk": True},
        "Jose Maria Gimenez": {"pos": "DEF", "role": "Centre Back", "pis": 8.7, "goal_share": 0.02, "def_impact": 0.22, "is_gk": False},
        "Robin Le Normand": {"pos": "DEF", "role": "Centre Back", "pis": 8.6, "goal_share": 0.02, "def_impact": 0.20, "is_gk": False},
        "Koke": {"pos": "MID", "role": "Captain / Central Midfield", "pis": 8.5, "goal_share": 0.03, "def_impact": 0.16, "is_gk": False},
        "Rodrigo De Paul": {"pos": "MID", "role": "Central Midfield", "pis": 8.5, "goal_share": 0.06, "def_impact": 0.14, "is_gk": False},
        "Conor Gallagher": {"pos": "MID", "role": "Midfield Engine", "pis": 8.3, "goal_share": 0.08, "def_impact": 0.14, "is_gk": False},
        "Marcos Llorente": {"pos": "DEF", "role": "Right Wingback", "pis": 8.5, "goal_share": 0.08, "def_impact": 0.14, "is_gk": False},
        "Samuel Lino": {"pos": "FWD", "role": "Left Wingback", "pis": 8.3, "goal_share": 0.10, "def_impact": 0.08, "is_gk": False},
        "Angel Correa": {"pos": "FWD", "role": "Impact Forward", "pis": 8.2, "goal_share": 0.14, "def_impact": 0.02, "is_gk": False}
    },
    "Athletic Bilbao": {
        "Nico Williams": {"pos": "FWD", "role": "Left Winger", "pis": 9.1, "goal_share": 0.24, "def_impact": 0.03, "is_gk": False},
        "Inaki Williams": {"pos": "FWD", "role": "Right Winger / Striker", "pis": 8.8, "goal_share": 0.25, "def_impact": 0.04, "is_gk": False},
        "Oihan Sancet": {"pos": "MID", "role": "Attacking Midfield", "pis": 8.7, "goal_share": 0.22, "def_impact": 0.06, "is_gk": False},
        "Dani Vivian": {"pos": "DEF", "role": "Centre Back", "pis": 8.5, "goal_share": 0.03, "def_impact": 0.20, "is_gk": False},
        "Unai Simon": {"pos": "GK", "role": "Goalkeeper (Spain No. 1)", "pis": 8.9, "goal_share": 0.00, "def_impact": 0.20, "is_gk": True},
        "Julen Agirrezabala": {"pos": "GK", "role": "Backup Goalkeeper", "pis": 8.0, "goal_share": 0.00, "def_impact": 0.12, "is_gk": True},
        "Gorka Guruzeta": {"pos": "FWD", "role": "Striker", "pis": 8.3, "goal_share": 0.20, "def_impact": 0.02, "is_gk": False},
        "Aitor Paredes": {"pos": "DEF", "role": "Centre Back", "pis": 8.2, "goal_share": 0.02, "def_impact": 0.16, "is_gk": False},
        "Yuri Berchiche": {"pos": "DEF", "role": "Left Back", "pis": 8.1, "goal_share": 0.03, "def_impact": 0.12, "is_gk": False}
    },
    "Real Sociedad": {
        "Martin Zubimendi": {"pos": "MID", "role": "Defensive Midfield", "pis": 9.0, "goal_share": 0.04, "def_impact": 0.22, "is_gk": False},
        "Takefusa Kubo": {"pos": "FWD", "role": "Right Winger", "pis": 8.8, "goal_share": 0.26, "def_impact": 0.04, "is_gk": False},
        "Mikel Oyarzabal": {"pos": "FWD", "role": "Forward (Captain)", "pis": 8.7, "goal_share": 0.25, "def_impact": 0.05, "is_gk": False},
        "Alex Remiro": {"pos": "GK", "role": "Goalkeeper", "pis": 8.4, "goal_share": 0.00, "def_impact": 0.18, "is_gk": True},
        "Robin Le Normand": {"pos": "DEF", "role": "Centre Back", "pis": 8.4, "goal_share": 0.02, "def_impact": 0.18, "is_gk": False},
        "Brais Mendez": {"pos": "MID", "role": "Attacking Midfield", "pis": 8.3, "goal_share": 0.14, "def_impact": 0.08, "is_gk": False}
    },

    # ==================== GERMAN BUNDESLIGA ====================
    "Bayern Munich": {
        "Harry Kane": {"pos": "FWD", "role": "Striker (Captain)", "pis": 9.8, "goal_share": 0.40, "def_impact": 0.02, "is_gk": False},
        "Jamal Musiala": {"pos": "MID", "role": "Attacking Midfield / Playmaker", "pis": 9.6, "goal_share": 0.22, "def_impact": 0.04, "is_gk": False},
        "Michael Olise": {"pos": "FWD", "role": "Right Winger", "pis": 9.0, "goal_share": 0.18, "def_impact": 0.03, "is_gk": False},
        "Joshua Kimmich": {"pos": "MID", "role": "Central Midfield / Leader", "pis": 9.2, "goal_share": 0.05, "def_impact": 0.20, "is_gk": False},
        "Dayot Upamecano": {"pos": "DEF", "role": "Centre Back", "pis": 8.6, "goal_share": 0.02, "def_impact": 0.20, "is_gk": False},
        "Min-jae Kim": {"pos": "DEF", "role": "Centre Back", "pis": 8.6, "goal_share": 0.02, "def_impact": 0.20, "is_gk": False},
        "Manuel Neuer": {"pos": "GK", "role": "Goalkeeper (Legend)", "pis": 8.8, "goal_share": 0.00, "def_impact": 0.18, "is_gk": True},
        "Alphonso Davies": {"pos": "DEF", "role": "Left Back", "pis": 8.8, "goal_share": 0.05, "def_impact": 0.14, "is_gk": False},
        "Serge Gnabry": {"pos": "FWD", "role": "Winger", "pis": 8.4, "goal_share": 0.14, "def_impact": 0.03, "is_gk": False},
        "Leroy Sane": {"pos": "FWD", "role": "Winger", "pis": 8.5, "goal_share": 0.14, "def_impact": 0.03, "is_gk": False},
        "Aleksandar Pavlovic": {"pos": "MID", "role": "Defensive Midfield", "pis": 8.4, "goal_share": 0.04, "def_impact": 0.16, "is_gk": False},
        "Joao Palhinha": {"pos": "MID", "role": "Defensive Midfield", "pis": 8.3, "goal_share": 0.02, "def_impact": 0.20, "is_gk": False},
        "Kingsley Coman": {"pos": "FWD", "role": "Winger", "pis": 8.2, "goal_share": 0.10, "def_impact": 0.02, "is_gk": False},
        "Thomas Muller": {"pos": "FWD", "role": "Raumdeuter", "pis": 8.2, "goal_share": 0.10, "def_impact": 0.04, "is_gk": False}
    },
    "Bayer Leverkusen": {
        "Florian Wirtz": {"pos": "MID", "role": "Attacking Midfield / Genius", "pis": 9.6, "goal_share": 0.28, "def_impact": 0.04, "is_gk": False},
        "Granit Xhaka": {"pos": "MID", "role": "Midfield General", "pis": 9.1, "goal_share": 0.06, "def_impact": 0.22, "is_gk": False},
        "Victor Boniface": {"pos": "FWD", "role": "Striker", "pis": 8.9, "goal_share": 0.30, "def_impact": 0.02, "is_gk": False},
        "Alex Grimaldo": {"pos": "DEF", "role": "Left Wingback / Dead-ball", "pis": 9.1, "goal_share": 0.18, "def_impact": 0.12, "is_gk": False},
        "Jeremie Frimpong": {"pos": "DEF", "role": "Right Wingback", "pis": 8.9, "goal_share": 0.16, "def_impact": 0.10, "is_gk": False},
        "Jonathan Tah": {"pos": "DEF", "role": "Centre Back (Captain)", "pis": 8.7, "goal_share": 0.04, "def_impact": 0.22, "is_gk": False},
        "Edmond Tapsoba": {"pos": "DEF", "role": "Centre Back", "pis": 8.5, "goal_share": 0.02, "def_impact": 0.18, "is_gk": False},
        "Piero Hincapie": {"pos": "DEF", "role": "Centre Back / LB", "pis": 8.4, "goal_share": 0.02, "def_impact": 0.16, "is_gk": False},
        "Lukas Hradecky": {"pos": "GK", "role": "Goalkeeper (Captain)", "pis": 8.4, "goal_share": 0.00, "def_impact": 0.16, "is_gk": True},
        "Robert Andrich": {"pos": "MID", "role": "Defensive Midfield", "pis": 8.3, "goal_share": 0.06, "def_impact": 0.18, "is_gk": False},
        "Patrik Schick": {"pos": "FWD", "role": "Striker", "pis": 8.4, "goal_share": 0.22, "def_impact": 0.01, "is_gk": False},
        "Martin Terrier": {"pos": "FWD", "role": "Forward", "pis": 8.1, "goal_share": 0.10, "def_impact": 0.02, "is_gk": False}
    },
    "Borussia Dortmund": {
        "Serhou Guirassy": {"pos": "FWD", "role": "Striker", "pis": 9.1, "goal_share": 0.36, "def_impact": 0.02, "is_gk": False},
        "Julian Brandt": {"pos": "MID", "role": "Attacking Midfield", "pis": 8.7, "goal_share": 0.16, "def_impact": 0.04, "is_gk": False},
        "Gregor Kobel": {"pos": "GK", "role": "Goalkeeper", "pis": 8.9, "goal_share": 0.00, "def_impact": 0.22, "is_gk": True},
        "Nico Schlotterbeck": {"pos": "DEF", "role": "Centre Back", "pis": 8.7, "goal_share": 0.04, "def_impact": 0.20, "is_gk": False},
        "Waldemar Anton": {"pos": "DEF", "role": "Centre Back", "pis": 8.3, "goal_share": 0.02, "def_impact": 0.16, "is_gk": False},
        "Pascal Gross": {"pos": "MID", "role": "Central Midfield", "pis": 8.4, "goal_share": 0.06, "def_impact": 0.14, "is_gk": False},
        "Marcel Sabitzer": {"pos": "MID", "role": "Box-to-box Midfield", "pis": 8.3, "goal_share": 0.10, "def_impact": 0.12, "is_gk": False},
        "Jamie Gittens": {"pos": "FWD", "role": "Winger", "pis": 8.4, "goal_share": 0.18, "def_impact": 0.02, "is_gk": False},
        "Donyell Malen": {"pos": "FWD", "role": "Forward / Winger", "pis": 8.2, "goal_share": 0.14, "def_impact": 0.02, "is_gk": False},
        "Karim Adeyemi": {"pos": "FWD", "role": "Speed Winger", "pis": 8.4, "goal_share": 0.16, "def_impact": 0.02, "is_gk": False},
        "Emre Can": {"pos": "MID", "role": "Captain / Defensive Midfield", "pis": 8.1, "goal_share": 0.04, "def_impact": 0.15, "is_gk": False}
    },
    "RB Leipzig": {
        "Xavi Simons": {"pos": "MID", "role": "Attacking Midfield / Playmaker", "pis": 9.2, "goal_share": 0.24, "def_impact": 0.04, "is_gk": False},
        "Lois Openda": {"pos": "FWD", "role": "Striker", "pis": 9.0, "goal_share": 0.35, "def_impact": 0.02, "is_gk": False},
        "Benjamin Sesko": {"pos": "FWD", "role": "Striker", "pis": 8.7, "goal_share": 0.26, "def_impact": 0.02, "is_gk": False},
        "Peter Gulacsi": {"pos": "GK", "role": "Goalkeeper", "pis": 8.5, "goal_share": 0.00, "def_impact": 0.18, "is_gk": True},
        "Willi Orban": {"pos": "DEF", "role": "Centre Back (Captain)", "pis": 8.6, "goal_share": 0.04, "def_impact": 0.22, "is_gk": False},
        "Castello Lukeba": {"pos": "DEF", "role": "Centre Back", "pis": 8.4, "goal_share": 0.01, "def_impact": 0.18, "is_gk": False},
        "David Raum": {"pos": "DEF", "role": "Left Wingback", "pis": 8.5, "goal_share": 0.06, "def_impact": 0.12, "is_gk": False},
        "Amadou Haidara": {"pos": "MID", "role": "Central Midfield", "pis": 8.2, "goal_share": 0.04, "def_impact": 0.14, "is_gk": False}
    },

    # ==================== ITALIAN SERIE A ====================
    "Inter": {
        "Lautaro Martinez": {"pos": "FWD", "role": "Striker (Captain)", "pis": 9.5, "goal_share": 0.35, "def_impact": 0.02, "is_gk": False},
        "Marcus Thuram": {"pos": "FWD", "role": "Striker", "pis": 9.1, "goal_share": 0.28, "def_impact": 0.03, "is_gk": False},
        "Nicolo Barella": {"pos": "MID", "role": "Midfield Dynamo", "pis": 9.2, "goal_share": 0.08, "def_impact": 0.18, "is_gk": False},
        "Hakan Calhanoglu": {"pos": "MID", "role": "Regista / Set-pieces", "pis": 9.1, "goal_share": 0.14, "def_impact": 0.16, "is_gk": False},
        "Alessandro Bastoni": {"pos": "DEF", "role": "Centre Back", "pis": 9.0, "goal_share": 0.03, "def_impact": 0.22, "is_gk": False},
        "Federico Dimarco": {"pos": "DEF", "role": "Left Wingback", "pis": 8.9, "goal_share": 0.12, "def_impact": 0.12, "is_gk": False},
        "Yann Sommer": {"pos": "GK", "role": "Goalkeeper", "pis": 8.7, "goal_share": 0.00, "def_impact": 0.20, "is_gk": True},
        "Benjamin Pavard": {"pos": "DEF", "role": "Centre Back", "pis": 8.5, "goal_share": 0.02, "def_impact": 0.18, "is_gk": False},
        "Francesco Acerbi": {"pos": "DEF", "role": "Centre Back", "pis": 8.3, "goal_share": 0.02, "def_impact": 0.18, "is_gk": False},
        "Henrikh Mkhitaryan": {"pos": "MID", "role": "Central Midfield", "pis": 8.3, "goal_share": 0.06, "def_impact": 0.12, "is_gk": False},
        "Denzel Dumfries": {"pos": "DEF", "role": "Right Wingback", "pis": 8.4, "goal_share": 0.08, "def_impact": 0.12, "is_gk": False},
        "Davide Frattesi": {"pos": "MID", "role": "Impact Midfield", "pis": 8.3, "goal_share": 0.14, "def_impact": 0.08, "is_gk": False},
        "Mehdi Taremi": {"pos": "FWD", "role": "Striker", "pis": 8.1, "goal_share": 0.15, "def_impact": 0.02, "is_gk": False}
    },
    "Juventus": {
        "Dusan Vlahovic": {"pos": "FWD", "role": "Striker", "pis": 9.2, "goal_share": 0.38, "def_impact": 0.02, "is_gk": False},
        "Kenan Yildiz": {"pos": "FWD", "role": "Winger / No. 10", "pis": 8.7, "goal_share": 0.18, "def_impact": 0.03, "is_gk": False},
        "Teun Koopmeiners": {"pos": "MID", "role": "Attacking Midfield", "pis": 8.9, "goal_share": 0.20, "def_impact": 0.10, "is_gk": False},
        "Gleison Bremer": {"pos": "DEF", "role": "Centre Back (Tower)", "pis": 9.1, "goal_share": 0.03, "def_impact": 0.26, "is_gk": False},
        "Michele Di Gregorio": {"pos": "GK", "role": "Goalkeeper", "pis": 8.6, "goal_share": 0.00, "def_impact": 0.18, "is_gk": True},
        "Manuel Locatelli": {"pos": "MID", "role": "Defensive Midfield", "pis": 8.4, "goal_share": 0.03, "def_impact": 0.18, "is_gk": False},
        "Andrea Cambiaso": {"pos": "DEF", "role": "Inverted Fullback", "pis": 8.5, "goal_share": 0.06, "def_impact": 0.14, "is_gk": False},
        "Pierre Kalulu": {"pos": "DEF", "role": "Centre Back", "pis": 8.3, "goal_share": 0.02, "def_impact": 0.16, "is_gk": False},
        "Weston McKennie": {"pos": "MID", "role": "Box-to-box Midfield", "pis": 8.2, "goal_share": 0.08, "def_impact": 0.12, "is_gk": False},
        "Francisco Conceicao": {"pos": "FWD", "role": "Right Winger", "pis": 8.3, "goal_share": 0.12, "def_impact": 0.02, "is_gk": False},
        "Nico Gonzalez": {"pos": "FWD", "role": "Winger", "pis": 8.2, "goal_share": 0.12, "def_impact": 0.04, "is_gk": False},
        "Federico Gatti": {"pos": "DEF", "role": "Centre Back", "pis": 8.2, "goal_share": 0.04, "def_impact": 0.16, "is_gk": False}
    },
    "Milan": {
        "Rafael Leao": {"pos": "FWD", "role": "Left Winger Superstar", "pis": 9.3, "goal_share": 0.26, "def_impact": 0.02, "is_gk": False},
        "Christian Pulisic": {"pos": "FWD", "role": "Right Winger / Playmaker", "pis": 9.1, "goal_share": 0.28, "def_impact": 0.04, "is_gk": False},
        "Theo Hernandez": {"pos": "DEF", "role": "Left Back Locomotive", "pis": 9.2, "goal_share": 0.14, "def_impact": 0.16, "is_gk": False},
        "Mike Maignan": {"pos": "GK", "role": "Goalkeeper", "pis": 9.0, "goal_share": 0.00, "def_impact": 0.22, "is_gk": True},
        "Alvaro Morata": {"pos": "FWD", "role": "Striker (Captain)", "pis": 8.6, "goal_share": 0.22, "def_impact": 0.04, "is_gk": False},
        "Tijjani Reijnders": {"pos": "MID", "role": "Central Midfield", "pis": 8.7, "goal_share": 0.12, "def_impact": 0.12, "is_gk": False},
        "Youssouf Fofana": {"pos": "MID", "role": "Defensive Midfield", "pis": 8.4, "goal_share": 0.03, "def_impact": 0.18, "is_gk": False},
        "Fikayo Tomori": {"pos": "DEF", "role": "Centre Back", "pis": 8.3, "goal_share": 0.02, "def_impact": 0.18, "is_gk": False},
        "Matteo Gabbia": {"pos": "DEF", "role": "Centre Back", "pis": 8.2, "goal_share": 0.03, "def_impact": 0.16, "is_gk": False},
        "Emerson Royal": {"pos": "DEF", "role": "Right Back", "pis": 7.9, "goal_share": 0.01, "def_impact": 0.12, "is_gk": False},
        "Tammy Abraham": {"pos": "FWD", "role": "Striker", "pis": 8.1, "goal_share": 0.14, "def_impact": 0.02, "is_gk": False},
        "Samuel Chukwueze": {"pos": "FWD", "role": "Winger", "pis": 8.0, "goal_share": 0.10, "def_impact": 0.02, "is_gk": False}
    },
    "Napoli": {
        "Khvicha Kvaratskhelia": {"pos": "FWD", "role": "Left Winger", "pis": 9.3, "goal_share": 0.26, "def_impact": 0.04, "is_gk": False},
        "Romelu Lukaku": {"pos": "FWD", "role": "Striker", "pis": 9.1, "goal_share": 0.32, "def_impact": 0.02, "is_gk": False},
        "Alessandro Buongiorno": {"pos": "DEF", "role": "Centre Back", "pis": 8.9, "goal_share": 0.03, "def_impact": 0.24, "is_gk": False},
        "Stanislav Lobotka": {"pos": "MID", "role": "Regista / DM", "pis": 8.9, "goal_share": 0.02, "def_impact": 0.18, "is_gk": False},
        "Alex Meret": {"pos": "GK", "role": "Goalkeeper", "pis": 8.4, "goal_share": 0.00, "def_impact": 0.16, "is_gk": True},
        "Scott McTominay": {"pos": "MID", "role": "Attacking / Box-to-box", "pis": 8.6, "goal_share": 0.16, "def_impact": 0.12, "is_gk": False},
        "Andre-Frank Zambo Anguissa": {"pos": "MID", "role": "Central Midfield", "pis": 8.5, "goal_share": 0.06, "def_impact": 0.16, "is_gk": False},
        "Amir Rrahmani": {"pos": "DEF", "role": "Centre Back", "pis": 8.3, "goal_share": 0.03, "def_impact": 0.16, "is_gk": False},
        "Giovanni Di Lorenzo": {"pos": "DEF", "role": "Right Back (Captain)", "pis": 8.6, "goal_share": 0.06, "def_impact": 0.15, "is_gk": False},
        "Mathias Olivera": {"pos": "DEF", "role": "Left Back", "pis": 8.2, "goal_share": 0.02, "def_impact": 0.12, "is_gk": False},
        "Matteo Politano": {"pos": "FWD", "role": "Right Winger", "pis": 8.3, "goal_share": 0.12, "def_impact": 0.06, "is_gk": False},
        "David Neres": {"pos": "FWD", "role": "Super-Sub Winger", "pis": 8.4, "goal_share": 0.15, "def_impact": 0.02, "is_gk": False}
    },
    "Atalanta": {
        "Mateo Retegui": {"pos": "FWD", "role": "Striker (Serie A Top Scorer)", "pis": 9.2, "goal_share": 0.38, "def_impact": 0.02, "is_gk": False},
        "Ademola Lookman": {"pos": "FWD", "role": "Forward / Ballon d'Or nominee", "pis": 9.3, "goal_share": 0.30, "def_impact": 0.03, "is_gk": False},
        "Charles De Ketelaere": {"pos": "FWD", "role": "Attacking Midfield", "pis": 8.7, "goal_share": 0.18, "def_impact": 0.04, "is_gk": False},
        "Ederson": {"pos": "MID", "role": "Central Midfield", "pis": 8.8, "goal_share": 0.08, "def_impact": 0.20, "is_gk": False},
        "Marten de Roon": {"pos": "MID", "role": "Midfield Anchor (Captain)", "pis": 8.4, "goal_share": 0.02, "def_impact": 0.20, "is_gk": False},
        "Isak Hien": {"pos": "DEF", "role": "Centre Back", "pis": 8.5, "goal_share": 0.01, "def_impact": 0.22, "is_gk": False},
        "Sead Kolasinac": {"pos": "DEF", "role": "Centre Back", "pis": 8.3, "goal_share": 0.02, "def_impact": 0.18, "is_gk": False},
        "Marco Carnesecchi": {"pos": "GK", "role": "Goalkeeper", "pis": 8.5, "goal_share": 0.00, "def_impact": 0.18, "is_gk": True},
        "Davide Zappacosta": {"pos": "DEF", "role": "Wingback", "pis": 8.2, "goal_share": 0.06, "def_impact": 0.12, "is_gk": False},
        "Mario Pasalic": {"pos": "MID", "role": "Attacking Midfield", "pis": 8.2, "goal_share": 0.12, "def_impact": 0.08, "is_gk": False}
    },

    # ==================== FRENCH LIGUE 1 ====================
    "Paris Saint-Germain": {
        "Ousmane Dembele": {"pos": "FWD", "role": "Winger / Playmaker", "pis": 9.1, "goal_share": 0.18, "def_impact": 0.03, "is_gk": False},
        "Bradley Barcola": {"pos": "FWD", "role": "Left Winger", "pis": 9.2, "goal_share": 0.32, "def_impact": 0.03, "is_gk": False},
        "Vitinha": {"pos": "MID", "role": "Central Midfield Anchor", "pis": 9.0, "goal_share": 0.08, "def_impact": 0.18, "is_gk": False},
        "Achraf Hakimi": {"pos": "DEF", "role": "Right Wingback", "pis": 9.1, "goal_share": 0.12, "def_impact": 0.12, "is_gk": False},
        "Gianluigi Donnarumma": {"pos": "GK", "role": "Goalkeeper", "pis": 9.0, "goal_share": 0.00, "def_impact": 0.20, "is_gk": True},
        "Marquinhos": {"pos": "DEF", "role": "Centre Back (Captain)", "pis": 8.8, "goal_share": 0.03, "def_impact": 0.20, "is_gk": False},
        "Willian Pacho": {"pos": "DEF", "role": "Centre Back", "pis": 8.5, "goal_share": 0.01, "def_impact": 0.18, "is_gk": False},
        "Nuno Mendes": {"pos": "DEF", "role": "Left Wingback", "pis": 8.7, "goal_share": 0.04, "def_impact": 0.12, "is_gk": False},
        "Joao Neves": {"pos": "MID", "role": "Midfield Engine", "pis": 8.8, "goal_share": 0.05, "def_impact": 0.18, "is_gk": False},
        "Warren Zaire-Emery": {"pos": "MID", "role": "Central Midfield", "pis": 8.5, "goal_share": 0.06, "def_impact": 0.14, "is_gk": False},
        "Fabian Ruiz": {"pos": "MID", "role": "Central Midfield", "pis": 8.4, "goal_share": 0.08, "def_impact": 0.10, "is_gk": False},
        "Marco Asensio": {"pos": "FWD", "role": "Forward / False 9", "pis": 8.2, "goal_share": 0.14, "def_impact": 0.02, "is_gk": False},
        "Randal Kolo Muani": {"pos": "FWD", "role": "Striker", "pis": 8.2, "goal_share": 0.16, "def_impact": 0.02, "is_gk": False},
        "Goncalo Ramos": {"pos": "FWD", "role": "Striker", "pis": 8.4, "goal_share": 0.22, "def_impact": 0.02, "is_gk": False},
        "Lucas Beraldo": {"pos": "DEF", "role": "Centre Back", "pis": 8.0, "goal_share": 0.01, "def_impact": 0.12, "is_gk": False}
    },
    "Monaco": {
        "Folarin Balogun": {"pos": "FWD", "role": "Striker", "pis": 8.6, "goal_share": 0.25, "def_impact": 0.02, "is_gk": False},
        "Aleksandr Golovin": {"pos": "MID", "role": "Attacking Midfield", "pis": 8.7, "goal_share": 0.18, "def_impact": 0.06, "is_gk": False},
        "Denis Zakaria": {"pos": "MID", "role": "Defensive Midfield (Captain)", "pis": 8.7, "goal_share": 0.08, "def_impact": 0.22, "is_gk": False},
        "Maghnes Akliouche": {"pos": "FWD", "role": "Winger / Playmaker", "pis": 8.6, "goal_share": 0.16, "def_impact": 0.04, "is_gk": False},
        "Eliesse Ben Seghir": {"pos": "MID", "role": "Attacking Midfield", "pis": 8.5, "goal_share": 0.18, "def_impact": 0.04, "is_gk": False},
        "Thilo Kehrer": {"pos": "DEF", "role": "Centre Back", "pis": 8.3, "goal_share": 0.04, "def_impact": 0.18, "is_gk": False},
        "Philipp Kohn": {"pos": "GK", "role": "Goalkeeper", "pis": 8.1, "goal_share": 0.00, "def_impact": 0.15, "is_gk": True},
        "Vanderson": {"pos": "DEF", "role": "Right Wingback", "pis": 8.3, "goal_share": 0.04, "def_impact": 0.12, "is_gk": False},
        "Breel Embolo": {"pos": "FWD", "role": "Striker", "pis": 8.2, "goal_share": 0.18, "def_impact": 0.02, "is_gk": False}
    },
    "Marseille": {
        "Mason Greenwood": {"pos": "FWD", "role": "Right Winger / Striker", "pis": 9.1, "goal_share": 0.35, "def_impact": 0.02, "is_gk": False},
        "Pierre-Emile Hojbjerg": {"pos": "MID", "role": "Midfield Anchor", "pis": 8.8, "goal_share": 0.04, "def_impact": 0.22, "is_gk": False},
        "Adrien Rabiot": {"pos": "MID", "role": "Central Midfield", "pis": 8.7, "goal_share": 0.10, "def_impact": 0.16, "is_gk": False},
        "Elye Wahi": {"pos": "FWD", "role": "Striker", "pis": 8.4, "goal_share": 0.22, "def_impact": 0.02, "is_gk": False},
        "Geronimo Rulli": {"pos": "GK", "role": "Goalkeeper", "pis": 8.3, "goal_share": 0.00, "def_impact": 0.18, "is_gk": True},
        "Leonardo Balerdi": {"pos": "DEF", "role": "Centre Back (Captain)", "pis": 8.4, "goal_share": 0.02, "def_impact": 0.20, "is_gk": False},
        "Amine Harit": {"pos": "MID", "role": "Attacking Midfield", "pis": 8.2, "goal_share": 0.10, "def_impact": 0.05, "is_gk": False},
        "Jonathan Rowe": {"pos": "FWD", "role": "Left Winger", "pis": 8.2, "goal_share": 0.14, "def_impact": 0.02, "is_gk": False}
    }
}

# Alias Paris SG to Paris Saint-Germain
EXPANDED_SQUAD_DATABASE["Paris SG"] = EXPANDED_SQUAD_DATABASE["Paris Saint-Germain"]
EXPANDED_SQUAD_DATABASE["Bayern München"] = EXPANDED_SQUAD_DATABASE["Bayern Munich"]

def resolve_canonical_club(team_name: str) -> str:
    """Resolves short names or aliases into canonical database keys."""
    cleaned = team_name.strip()
    if cleaned in EXPANDED_SQUAD_DATABASE:
        return cleaned
    if cleaned in CLUB_ALIASES:
        return CLUB_ALIASES[cleaned]
    # Fuzzy match
    for alias, canonical in CLUB_ALIASES.items():
        if alias.lower() in cleaned.lower() or cleaned.lower() in alias.lower():
            return canonical
    for canonical in EXPANDED_SQUAD_DATABASE:
        if canonical.lower() in cleaned.lower() or cleaned.lower() in canonical.lower():
            return canonical
    return cleaned

def generate_default_squad(team_name: str) -> Dict[str, Dict[str, Any]]:
    """Generates a realistic active starter roster if a team is not in the expanded database."""
    return {
        f"Starting Striker ({team_name})": {"pos": "FWD", "role": "Striker", "pis": 8.2, "goal_share": 0.28, "def_impact": 0.02, "is_gk": False},
        f"Key Winger ({team_name})": {"pos": "FWD", "role": "Winger", "pis": 8.0, "goal_share": 0.18, "def_impact": 0.03, "is_gk": False},
        f"Attacking Playmaker ({team_name})": {"pos": "MID", "role": "Attacking Midfield", "pis": 8.1, "goal_share": 0.14, "def_impact": 0.06, "is_gk": False},
        f"Defensive Midfield Anchor ({team_name})": {"pos": "MID", "role": "Defensive Midfield", "pis": 8.0, "goal_share": 0.04, "def_impact": 0.18, "is_gk": False},
        f"Box-to-Box Midfielder ({team_name})": {"pos": "MID", "role": "Central Midfield", "pis": 7.9, "goal_share": 0.08, "def_impact": 0.12, "is_gk": False},
        f"Lead Centre Back / Captain ({team_name})": {"pos": "DEF", "role": "Centre Back", "pis": 8.2, "goal_share": 0.03, "def_impact": 0.20, "is_gk": False},
        f"Second Centre Back ({team_name})": {"pos": "DEF", "role": "Centre Back", "pis": 7.9, "goal_share": 0.02, "def_impact": 0.16, "is_gk": False},
        f"Starting Left Back ({team_name})": {"pos": "DEF", "role": "Fullback", "pis": 7.8, "goal_share": 0.02, "def_impact": 0.11, "is_gk": False},
        f"Starting Right Back ({team_name})": {"pos": "DEF", "role": "Fullback", "pis": 7.8, "goal_share": 0.02, "def_impact": 0.11, "is_gk": False},
        f"Primary Goalkeeper ({team_name})": {"pos": "GK", "role": "Goalkeeper", "pis": 8.1, "goal_share": 0.00, "def_impact": 0.18, "is_gk": True},
        f"Backup Goalkeeper ({team_name})": {"pos": "GK", "role": "Backup Goalkeeper", "pis": 7.3, "goal_share": 0.00, "def_impact": 0.08, "is_gk": True}
    }

def get_club_squad(team_name: str) -> Dict[str, Dict[str, Any]]:
    """Returns squad roster dictionary for a given team, with alias and fuzzy matching."""
    canon = resolve_canonical_club(team_name)
    if canon in EXPANDED_SQUAD_DATABASE:
        return EXPANDED_SQUAD_DATABASE[canon]
    return generate_default_squad(team_name)

def get_squad_player_names(team_name: str) -> List[str]:
    """Returns list of player names with role information formatted for UI dropdowns."""
    squad = get_club_squad(team_name)
    # Return formatted "Name (Role - Position)"
    return [f"{name} ({data['role']})" for name, data in squad.items()]
