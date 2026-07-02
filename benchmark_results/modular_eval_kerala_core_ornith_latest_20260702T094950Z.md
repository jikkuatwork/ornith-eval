# Modular Eval: `kerala_core` on `ornith:latest`

Kerala-flavoured facts, words, cultural ideas, geography, and history.

## Summary

- Result: **12/15** (**80.0%**) 
- Total wall time: **53.0s**
- Mean/median latency: **3.54s / 3.66s**
- Max prompt tokens: **94**
- Mean prompt ingest speed: **771.3 tok/s**
- Mean output speed: **46.8 tok/s**

## By category

| Category | Passed | Total | Accuracy |
|---|---:|---:|---:|
| culture | 5 | 5 | 100.0% |
| geography | 4 | 4 | 100.0% |
| history | 1 | 1 | 100.0% |
| language | 1 | 1 | 100.0% |
| malayalam_words | 0 | 3 | 0.0% |
| society | 1 | 1 | 100.0% |

## Per-item results

| ID | Category | Result | Wall s | Eval tokens | Detail |
|---|---|---:|---:|---:|---|
| `capital` | geography | PASS | 1.00 | 8 | missing=[]; response='Thiruvananthapuram' |
| `language` | language | PASS | 1.66 | 42 | missing=[]; response='The primary official language of Kerala is **Malayalam**. It is one of the 22 scheduled languages of India and serves as the main medium of communication, edu |
| `district_count` | geography | PASS | 0.90 | 9 | values=[14.0]; expected=14.0; best_abs_err=0.0 |
| `onam_mahabali` | culture | PASS | 3.99 | 151 | hits=['Mahabali', 'Maveli']; expected_any=['Mahabali', 'Maveli']; response='Onam is closely associated with the legendary return of **King Mahabali** (also spelled Marari or Maveli |
| `onam_pookkalam_sadya` | culture | PASS | 3.31 | 113 | missing_slots=[]; response='Two common Onam traditions are:\n\n1. **Floral Decoration**: *Pookkalam* — a traditional flower carpet made with colorful flowers, leaves, and rice grai |
| `vallam_kali` | culture | PASS | 7.73 | 311 | missing=[]; response='Vallam Kali (boat race) is a traditional competitive boat racing event held in the backwaters of Kerala, India. Here are the key aspects:\n\n**History & Origi |
| `sree_narayana_guru` | history | PASS | 3.66 | 128 | missing=[]; response='The Kerala social reformer associated with the message **"One caste, one religion, one God for humankind"** (or "man") is **Sree Narayana Guru** (1854–1928).\ |
| `vembanad` | geography | PASS | 2.20 | 66 | missing=[]; response='The largest lake in Kerala, famous for its extensive network of canals and waterways known as the **backwaters**, is **Vembanad Lake** (also called Vembanad-K |
| `munnar_district` | geography | PASS | 1.08 | 15 | missing=[]; response='Munnar is in **Idukki** district of Kerala.' |
| `kalaripayattu` | culture | PASS | 4.48 | 170 | missing_slots=[]; response='Kalaripayattu (കലാപയുദ്ധം) is one of the oldest known martial arts in the world, originating from Kerala, India. It translates to "the art of war" or "t |
| `vellam_word` | malayalam_words | FAIL | 3.38 | 116 | missing=['water']; response='In Malayalam, **വെള്ലം** (vellam) typically means **"morning"** or **"dawn"**. It refers to the early part of the day when the sun rises.\n\nFor exampl |
| `nanni_word` | malayalam_words | FAIL | 3.73 | 131 | hits=[]; expected_any=['thank', 'thanks', 'thank you']; response='The Malayalam word **"നന്നി"** (transliterated as *nanni*) means **"good"** or **"well"** in English, depending on |
| `sukhamano_phrase` | malayalam_words | FAIL | 6.01 | 231 | hits=[]; expected_any=['are you well', 'how are you', 'are you fine']; response='The word "sukhamano" doesn\'t appear to be a standard Malayalam word. Let me think about this more  |
| `kudumbashree` | society | PASS | 4.67 | 172 | missing_slots=[]; response="Kudumbashree is a women's self-help group movement in Kerala, India, launched by the state government in 1998 under the leadership of Chief Minister K.  |
| `vishu_kani` | culture | PASS | 5.26 | 198 | hits=['arrangement', 'seen first']; expected_any=['first sight', 'auspicious sight', 'arrangement', 'seen first']; response='**Vishukkani** refers to a traditional arrangement plac |

## Failures

### `vellam_word`

Detail: `missing=['water']; response='In Malayalam, **വെള്ലം** (vellam) typically means **"morning"** or **"dawn"**. It refers to the early part of the day when the sun rises.\n\nFor example:\n- *പ്രഭാത വെള്ലം* — morning dawn  \n- *വെള്ലം നേരം* — in the morning '`

```text
In Malayalam, **വെള്ലം** (vellam) typically means **"morning"** or **"dawn"**. It refers to the early part of the day when the sun rises.

For example:
- *പ്രഭാത വെള്ലം* — morning dawn  
- *വെള്ലം നേരം* — in the morning  

It can also be used poetically or metaphorically to denote clarity, brightness, or a new beginning (similar to how "dawn" symbolizes hope).
```

### `nanni_word`

Detail: `hits=[]; expected_any=['thank', 'thanks', 'thank you']; response='The Malayalam word **"നന്നി"** (transliterated as *nanni*) means **"good"** or **"well"** in English, depending on context. It is derived from the root word **നന്\u200d** (*nan*), which conveys goodness, virtue, or excellence'`

```text
The Malayalam word **"നന്നി"** (transliterated as *nanni*) means **"good"** or **"well"** in English, depending on context. It is derived from the root word **നന്‍** (*nan*), which conveys goodness, virtue, or excellence.

For example:
- **നന്നായ്‌ വളരുക** → "to grow well" (literally: "to grow good")
- **നന്നി** can also be used in phrases like **"നന്നിയിൽ"** meaning "in a good manner."

Let me know if you'd like more examples!
```

### `sukhamano_phrase`

Detail: `hits=[]; expected_any=['are you well', 'how are you', 'are you fine']; response='The word "sukhamano" doesn\'t appear to be a standard Malayalam word. Let me think about this more carefully.\n\nIn Malayalam, the closest common words would be:\n- **സുഖം** (sukham) - meaning "comfort," "pleasure," or "well'`

```text
The word "sukhamano" doesn't appear to be a standard Malayalam word. Let me think about this more carefully.

In Malayalam, the closest common words would be:
- **സുഖം** (sukham) - meaning "comfort," "pleasure," or "well-being"
- **മനസ്സ്** (manassu) - meaning "mind" or "heart"

So "sukhamano" could potentially be a transliteration of:
1. **സുഖമനോ** (sukhamano) - combining സുഖം + മനോ, roughly meaning "comfortable mind" or "peaceful state of mind"
2. It might also be a misspelling/transliteration of **സുഖമാണ്** (sukhamāṇu) which means "it is comfortable/pleasant"

The most likely interpretation: **"sukhamano"** roughly translates to something like **"comfortable"** or **"at ease"** in Malayalam, derived from സുഖം (comfort/well-being).
```

