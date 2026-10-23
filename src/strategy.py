"""
IncuBrix Strategy Module
Defines content pillars, platform personas, and tone mappings.
"""

from typing import Dict, List

CONTENT_PILLARS: Dict[str, Dict[str, str]] = {
    "creator_workflow": {
        "name": "Creator Workflow Education",
        "description": "Standard operating procedures, time-saving systems, and frameworks to eliminate content burnout.",
        "best_platforms": ["linkedin", "instagram", "youtube"]
    },
    "repurposing_productivity": {
        "name": "Content Repurposing & Productivity",
        "description": "Systematic 1-to-30 multiplication frameworks turning long-form blogs, podcasts, and videos into multi-channel assets.",
        "best_platforms": ["linkedin", "instagram", "youtube"]
    },
    "practical_tutorials": {
        "name": "Practical Tutorials & Demonstrations",
        "description": "Step-by-step guides showing tactical execution, prompt engineering, and pipeline automation.",
        "best_platforms": ["youtube", "linkedin", "instagram"]
    },
    "creator_challenges": {
        "name": "Creator Challenges & Common Mistakes",
        "description": "Exposing flawed creator habits (e.g., lazy copy-pasting, neglecting UTMs, lack of hooks) and offering solutions.",
        "best_platforms": ["instagram", "linkedin", "youtube"]
    },
    "responsible_ai": {
        "name": "Responsible AI & Content Quality",
        "description": "Fact-checking, human editorial oversight, brand safety, and ethical AI-assisted creation.",
        "best_platforms": ["linkedin", "youtube"]
    },
    "verified_product_demos": {
        "name": "Verified Product Demos & Use Cases",
        "description": "Concrete demonstrations of the IncuBrix Creator OS turning core inputs into scheduled outputs.",
        "best_platforms": ["linkedin", "instagram", "youtube"]
    }
}

PLATFORM_PROFILES: Dict[str, Dict[str, any]] = {
    "linkedin": {
        "audience": "Knowledge workers, content agency founders, B2B marketers, and professional solopreneurs",
        "primary_formats": ["li_post", "li_carousel"],
        "tone_emphasis": "Professional, framework-driven, analytical, actionable",
        "max_hashtags": 5,
        "default_cta": "Explore how IncuBrix automates this workflow: https://incubrix.com"
    },
    "instagram": {
        "audience": "Visual creators, digital entrepreneurs, video makers, and personal brands",
        "primary_formats": ["ig_reel", "ig_carousel", "ig_graphic"],
        "tone_emphasis": "High energy, punchy, visually dynamic, relatable",
        "max_hashtags": 10,
        "default_cta": "Save this post and visit incubrix.com for the full system breakdown."
    },
    "youtube": {
        "audience": "Self-directed learners, digital builders, video creators, and tech enthusiasts",
        "primary_formats": ["yt_short", "yt_community"],
        "tone_emphasis": "Curiosity-sparking, immediate pacing, punchy hooks, clear takeaways",
        "max_hashtags": 4,
        "default_cta": "Watch your content engine scale at incubrix.com (link in pinned comment)."
    }
}


def get_pillar_list() -> List[str]:
    return [p["name"] for p in CONTENT_PILLARS.values()]


def get_pillar_by_key_or_name(key_or_name: str) -> str:
    for k, v in CONTENT_PILLARS.items():
        if k == key_or_name or v["name"].lower() == key_or_name.lower():
            return v["name"]
    return CONTENT_PILLARS["creator_workflow"]["name"]
