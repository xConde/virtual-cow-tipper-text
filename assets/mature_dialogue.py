"""
Mature dialogue additions - Adult humor, dry wit, sophisticated jokes.
Use INSTEAD of overly punny dialogue from context.py

Mix ratio: 70% from here (mature), 30% from context.py (puns)
"""

# Sophisticated cow sayings with less pun density
mature_cow_sayings = {
    'friendly': {
        'intro': [
            "Well, hello there. You look like someone who appreciates a good business transaction.",
            "Listen, I don't usually do this, but you seem alright. How about a tip?",
            "You know what? I like your energy. Let's skip the small talk - you got cash?",
            "I've been standing here for hours. You're literally the most interesting thing that's happened today.",
            "Okay, real talk - I'm a cow. You're a human. This is weird for both of us. But tips make it less weird.",
            "I'm going to be straight with you: I could use the money. The economy's rough out here.",
            # Keep ONE good pun for contrast
            "I hate to milk this moment, but... actually, I don't hate it at all. Tips?",
        ],
        'counter': [
            "I mean... it's something. Not exactly retirement money, but sure.",
            "That's what we're doing? Okay. Fine. I'll take it.",
            "You know what, I respect the honesty. It's not great, but you tried.",
            "Could be worse. Could be better. But mainly could be more.",
            "I'm choosing to interpret this as 'generous' in your local currency.",
        ],
        'graceful': [
            "Okay, NOW we're talking. That's what I'm talking about!",
            "See? Was that so hard? This is what I call a proper transaction.",
            "You just made my entire week. Possibly month. The bar's pretty low out here.",
            "THAT'S how you tip a cow! Take notes, everyone!",
            "I... wow. I'm genuinely impressed. And I'm not easily impressed.",
        ],
    },
    'neutral': {
        'intro': [
            "Yeah?",
            "You need something, or are you just window shopping for cows?",
            "Let me guess - you want to tip me. Everyone wants to tip me. It's like I'm famous or something.",
            "I'm a cow. You're here. What now?",
            "I don't do autographs, if that's what you're wondering.",
            "This again. Alright, let's get this over with.",
        ],
        'counter': [
            "That's it? Wow. Okay.",
            "I've received worse, I suppose.",
            "Cool. Great. Fantastic. Moving on.",
            "Is this a joke? Because I'm not laughing.",
            "You know what, I'm not even mad. Just disappointed.",
        ],
        'graceful': [
            "Huh. Actually decent. Color me surprised.",
            "You know what? That'll do. That'll do.",
            "I... actually respect that. Didn't see it coming.",
            "Alright, you've earned a modicum of my respect.",
            "Not bad. Not bad at all. You might actually know what you're doing.",
        ],
    },
    'upset': {
        'intro': [
            "What. Do. You. Want.",
            "I've had a DAY. Unless you're here to make it better, keep moving.",
            "Oh great. Another human. This is exactly what I needed right now.",
            "I'm about two seconds away from a complete breakdown. Make this quick.",
            "You picked the WRONG cow on the WRONG day.",
            "I don't have time for this. I don't have time for ANY of this.",
        ],
        'counter': [
            "Are you kidding me? THAT'S your offer?",
            "You know what? Fine. Whatever. I don't even care anymore.",
            "This is exactly the kind of day I'm having. Exactly this.",
            "I should've stayed in bed. Or barn. Whatever.",
            "You're lucky I'm too tired to be more upset about this.",
        ],
        'graceful': [
            "...Fine. You got me. That's actually acceptable.",
            "Okay, I'll admit it - that helps. Slightly.",
            "You know what, maybe you're not completely terrible.",
            "I guess I can't stay mad. Not at THAT tip anyway.",
            "This doesn't fix my day, but it's a start.",
        ],
        'shop_keeper_intro': [
            "Welcome to my shop. Prices are non-negotiable. Don't ask.",
            "Yes, I'm a cow. Yes, I run a business. We've established this. Buy something or don't.",
            "Make it quick. I have inventory to restock and existential crises to process.",
            "Shop's open. My patience is not. What do you need?",
        ],
        'shop_keeper_purchase': [
            "Fine. It's yours. Now leave.",
            "Money received. Transaction complete. Goodbye.",
            "Great. Another sale. My life is complete. *sarcasm*",
        ],
    }
}

# Dark humor combat contexts
mature_combat_contexts = {
    'small_damage': [
        "{player_name} lands a glancing blow. {cow_name} looks mildly annoyed.",
        "That barely registered. {cow_name} seems unimpressed.",
        "{player_name} strikes for {total_damage} damage. {cow_name} yawns.",
        "A weak hit. This is going to take a while.",
    ],
    'large_damage': [
        "{player_name} connects with brutal force. {cow_name} reels from {total_damage} damage.",
        "WHAM! {total_damage} damage. That definitely hurt.",
        "{player_name} strikes true. {cow_name} staggers, clearly hurting.",
        "Critical hit for {total_damage}. This fight just got serious.",
    ],
    'victory': [
        "{cow_name} collapses. Another day, another cow tipped.",
        "Victory. {cow_name} won't be getting up from that one.",
        "{cow_name} is down. You're getting disturbingly good at this.",
        "And that's that. {cow_name} has been thoroughly tipped.",
    ],
    'player_death': [
        "You've been thoroughly trampled. This is embarrassing.",
        "And that's how your story ends. Trampled by livestock.",
        "The cow wins. You lose. Tale as old as time.",
    ]
}

# Sophisticated/Literary cow names (replace some basic ones)
mature_cow_names = [
    "Sartre",      # Existentialist philosopher
    "Camus",       # Absurdist philosopher
    "Kafka",       # Surrealist author
    "Plato",       # Classical philosopher
    "Nietzsche",   # "God is dead" guy
    "Foucault",    # French philosopher
    "Dostoevsky",  # Russian novelist
    "Voltaire",    # French writer
    "Orwell",      # 1984 author
    "Vonnegut",    # Dark humor author
]

# Existential/philosophical cow approaches
mature_approaches = [
    "A cow stares into the void. The void stares back. The cow is unimpressed.",
    "You encounter a cow reading Nietzsche. It mutters 'God is dead, and so is my will to live.'",
    "A cow sits motionless, contemplating the futility of existence in a field.",
    "You find a cow that seems to be having an existential crisis. It's not handling it well.",
    "A cow is writing '1984' in the dirt. Big Brother is watching. Big Brother is always watching.",
    "You encounter a cow practicing nihilism. Nothing matters, it explains. Especially not tips.",
    "A cow appears to be staging a one-cow production of 'Waiting for Godot.' Godot never shows up.",
]
