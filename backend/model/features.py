"""
features.py — Text Feature Engineering for Fake Review Detection
Extracts handcrafted linguistic features from raw review text.
"""

import re
import string
import numpy as np


# Common English stopwords (lightweight — no NLTK dependency needed)
_STOPWORDS = {
    "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your",
    "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", "her",
    "hers", "herself", "it", "its", "itself", "they", "them", "their", "theirs",
    "themselves", "what", "which", "who", "whom", "this", "that", "these", "those",
    "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
    "having", "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if",
    "or", "because", "as", "until", "while", "of", "at", "by", "for", "with",
    "about", "against", "between", "through", "during", "before", "after", "above",
    "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under",
    "again", "further", "then", "once", "here", "there", "when", "where", "why",
    "how", "all", "both", "each", "few", "more", "most", "other", "some", "such",
    "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s",
    "t", "can", "will", "just", "don", "should", "now", "d", "ll", "m", "o", "re",
    "ve", "y", "ain", "aren", "couldn", "didn", "doesn", "hadn", "hasn", "haven",
    "isn", "ma", "mightn", "mustn", "needn", "shan", "shouldn", "wasn", "weren",
    "won", "wouldn",
}


def _count_syllables(word: str) -> int:
    """Rough syllable count using vowel-group heuristic."""
    word = word.lower().strip()
    if not word:
        return 0
    vowels = "aeiou"
    count = 0
    prev_vowel = False
    for ch in word:
        if ch in vowels:
            if not prev_vowel:
                count += 1
            prev_vowel = True
        else:
            prev_vowel = False
    # Words like "the" should have at least 1 syllable
    return max(1, count)


def extract_handcrafted_features(text: str) -> np.ndarray:
    """
    Extract a set of linguistic and stylistic features from review text.
    Returns a 1D numpy array of 25 features.
    """
    text = str(text)

    # --- Length features ---
    char_count = len(text)
    word_count = len(text.split())
    avg_word_length = (
        sum(len(w) for w in text.split()) / word_count if word_count > 0 else 0
    )
    sentence_count = max(1, len(re.split(r"[.!?]", text)))
    avg_sentence_length = word_count / sentence_count

    # --- Punctuation features ---
    exclamation_count = text.count("!")
    question_count = text.count("?")
    ellipsis_count = text.count("...")

    # --- Case features ---
    upper_chars = sum(1 for c in text if c.isupper())
    caps_ratio = upper_chars / char_count if char_count > 0 else 0
    all_caps_words = sum(1 for w in text.split() if w.isupper() and len(w) > 1)

    # --- Repetition features ---
    words = text.lower().split()
    unique_ratio = len(set(words)) / len(words) if words else 0

    # --- First-person usage (common in genuine reviews) ---
    first_person = len(
        re.findall(r"\b(i|me|my|myself|mine|we|our|ours|ourselves)\b", text.lower())
    )

    # --- Superlative/extreme language (common in fake reviews) ---
    superlatives = len(
        re.findall(
            r"\b(best|worst|amazing|terrible|perfect|horrible|excellent|awful|greatest|fantastic)\b",
            text.lower(),
        )
    )

    # --- Generic phrases (commonly seen in fake reviews) ---
    generic_phrases = len(
        re.findall(
            r"\b(great product|love it|highly recommend|five stars|must buy|worth the money)\b",
            text.lower(),
        )
    )

    # =========================================================
    # NEW FEATURES (12 additional)
    # =========================================================

    # --- Digit ratio: fake reviews often lack specific numbers ---
    digit_chars = sum(1 for c in text if c.isdigit())
    digit_ratio = digit_chars / char_count if char_count > 0 else 0

    # --- Punctuation density ---
    punct_chars = sum(1 for c in text if c in string.punctuation)
    punctuation_density = punct_chars / char_count if char_count > 0 else 0

    # --- Repeated characters: e.g. "sooooo goooood" ---
    repeated_char_count = len(re.findall(r"(.)\1{2,}", text))

    # --- URL count: genuine reviews rarely contain URLs ---
    url_count = len(re.findall(r"http\S+|www\.\S+", text))

    # --- Emoji-like pattern count ---
    emoji_count = len(re.findall(r"[:;][-']?[)(DP/\\|]|[<>]{2}", text))

    # --- Stopword ratio: fake reviews tend to use fewer stopwords ---
    stopword_count = sum(1 for w in words if w in _STOPWORDS)
    stopword_ratio = stopword_count / len(words) if words else 0

    # --- Capital word ratio ---
    capital_word_ratio = all_caps_words / word_count if word_count > 0 else 0

    # --- Average syllables per word (readability proxy) ---
    syllable_counts = [_count_syllables(w) for w in text.split()]
    avg_syllables = (
        sum(syllable_counts) / len(syllable_counts) if syllable_counts else 0
    )

    # --- Sentence length variance (complexity measure) ---
    sentences = [s.strip() for s in re.split(r"[.!?]", text) if s.strip()]
    if len(sentences) > 1:
        sent_lengths = [len(s.split()) for s in sentences]
        sentence_complexity = float(np.std(sent_lengths))
    else:
        sentence_complexity = 0.0

    # --- Hedge words: "maybe", "perhaps", "kind of" — genuine signal ---
    hedge_word_count = len(
        re.findall(
            r"\b(maybe|perhaps|possibly|probably|might|could|seems?|somewhat|kind of|sort of|a bit|a little|i think|i guess|not sure)\b",
            text.lower(),
        )
    )

    # --- Urgency words: "buy now", "hurry", "limited" — fake signal ---
    urgency_word_count = len(
        re.findall(
            r"\b(buy now|hurry|limited|act fast|don't miss|order now|best deal|last chance|only today|exclusive|must have|grab|rush)\b",
            text.lower(),
        )
    )

    # --- Review specificity: presence of specific details ---
    specificity = len(
        re.findall(
            r"\b(\d+\s*(inch|cm|mm|lb|kg|oz|gb|mb|hours?|days?|weeks?|months?|years?|dollars?|bucks?))\b",
            text.lower(),
        )
    )

    features = np.array(
        [
            # Original 13
            char_count,
            word_count,
            avg_word_length,
            avg_sentence_length,
            exclamation_count,
            question_count,
            ellipsis_count,
            caps_ratio,
            all_caps_words,
            unique_ratio,
            first_person,
            superlatives,
            generic_phrases,
            # New 12
            digit_ratio,
            punctuation_density,
            repeated_char_count,
            url_count,
            emoji_count,
            stopword_ratio,
            capital_word_ratio,
            avg_syllables,
            sentence_complexity,
            hedge_word_count,
            urgency_word_count,
            specificity,
        ],
        dtype=float,
    )

    return features


FEATURE_NAMES = [
    # Original 13
    "char_count",
    "word_count",
    "avg_word_length",
    "avg_sentence_length",
    "exclamation_count",
    "question_count",
    "ellipsis_count",
    "caps_ratio",
    "all_caps_words",
    "unique_word_ratio",
    "first_person_count",
    "superlative_count",
    "generic_phrase_count",
    # New 12
    "digit_ratio",
    "punctuation_density",
    "repeated_char_count",
    "url_count",
    "emoji_count",
    "stopword_ratio",
    "capital_word_ratio",
    "avg_syllables_per_word",
    "sentence_complexity",
    "hedge_word_count",
    "urgency_word_count",
    "review_specificity",
]
