# Case study: Commons Quest

*Chris Garceau · product owner, designer and builder (with an AI coding agent) · fall 2026*

## 1. The problem

I eat at Berkshire most days and lift, so I aim for about 3,400 calories and 170 g of protein a day. UMass publishes the nutrition and allergens for every dish, but the only way to use them was to open each hall's menu, scroll stations and do the math in my head. MyFitnessPal doesn't know the dining hall menus, so every meal meant typing in foods by hand. I wanted a replacement that already knew every food I could eat on campus.

The official UMass Dining app shows menus, hours, crowd levels and allergen filters. But it doesn't know your goals, doesn't track your day and doesn't tell you what to eat. When I checked, it had 26 ratings on the App Store.

**Who has this problem:**

| Student | What they need | What fails them today |
|---|---|---|
| Athletes and gym-goers | Hit protein and calories every day | Doing the math across four menus; generic trackers |
| Students with allergies or a diet (halal, vegan, vegetarian) | Know what's safe at *this* hall, *now* | Checking labels dish by dish |
| Freshmen and transfer students | Know where to go and what's good | Nothing personalized |
| Anyone trying to eat better | A reason to keep going after week one | Logging is a chore with no payoff |

## 2. The bet

*If logging takes seconds and feels like a game, students keep doing it. And if the app knows their goals, diet and allergies, its suggestions are worth opening it for.*

**Design principles:**
1. **Seconds, not minutes.** Tap + on a suggestion, or type a sentence. Never search a database.
2. **Personal from minute one.** Usual hall, diet, allergies and which stats you track are asked once and respected everywhere. A demo mode lets someone look around before committing.
3. **Reward consistency, not restriction.** Calories are something to *reach*, the boss's HP, not a limit to stay under. Goals have a safe floor of 1,200 kcal. The app never shames.
4. **Your data is yours.** No accounts and no tracking. The log lives on the phone.
5. **$0 to run, so it can't die when a free trial ends.**

## 3. Key decisions and trade-offs

| Decision | Why | What I gave up |
|---|---|---|
| Gamify with pixel-art bosses (one per dining hall) | The hook is the reason people come back tomorrow. Each hall's boss gives it an identity students recognize | Weeks of art iteration. I went through about 10 rounds on character design alone |
| Static site + nightly GitHub Action instead of a server | Free, fast and nothing to maintain. The data changes once a day anyway | Real-time crowd levels. UMass's feed can't be read from a browser (no CORS) |
| On-device meal parser instead of an LLM API | $0 per user, works offline, instant, private | Less flexible than an LLM with unusual phrasing. Mitigated with a "not it? swap" button showing alternatives |
| Log stays on the phone (localStorage), with file backup/restore | Privacy, and no accounts to sign up for | No automatic sync across devices |
| Show allergen warnings *and* hide those foods from suggestions | Safety. A warning you can see beats a filter you have to trust | A busier list. I made the tags quiet except for allergens |
| Calorie floor and "eat enough" framing | Responsible design for a food app aimed at 18–22 year olds | Users who want aggressive cuts are told to see a professional |
| No selling or sharing of user data. Any future insights for UMass Dining would be opt-in, anonymous and aggregated | Food logs are health data, and trust is the product | A potential revenue line |

## 4. What I built

- About 2,200 campus foods: 14 days of menus for 4 dining commons and 25 cafés, nutrition, allergens, diet flags and today's hours, refreshed nightly with validation.
- Setup (character, usual hall, diet, allergies, goal presets) and a home screen with a daily quest, a "next move" combo for your hall and meal, **Your Usuals** and faves.
- Learning: foods you log rank higher, and ✕ removes a suggestion forever.
- A quick log that parses quantities, units, slang ("choc milk", "pep za"), typos and hall hints.
- Boss fights with per-hall backdrops and hit, crit and KO effects. A 3/4-view campus map rebuilt from the official map's vector data, with day, night and winter versions.
- A home-screen app (PWA) that works offline, plus backup and restore.
- Unit and end-to-end tests that run on every push.

## 5. Launch plan and how I'll measure it

Status: live, pre-launch. Next is a one-week soft launch with about 10 friends, fixing what they run into, then a wider post to UMass students. Alongside it: a 5-question survey and 5 short conversations about how students decide what to eat.

| Metric | Target |
|---|---|
| Students who finish setup | 100 in the first 2 weeks |
| Come back a second day (D1 retention) | 40% |
| Still logging after a week (D7) | 20% |
| Meals logged per active user per day | 2+ |
| Share of logs that use quick log vs. tapping + | Tracked to see if typing beats tapping |

## 6. What I learned

- Building for myself first meant a lot of my own habits were baked in: a fixed calorie target to *reach*, and protein, sugar and sodium as the only stats. Making it work for anyone meant letting people pick what they track, and letting a cut or maintenance goal win by landing *near* the target instead of past it.
- Building with an AI agent changed what my job was. The hard part wasn't code. It was being specific about what "good" looks like and checking the output with my own eyes every round.

## 7. What's next

- Anonymous, opt-in demand insights for UMass Dining, for example "vegetarian students can't hit protein at Hampshire on Tuesdays", to help cut food waste and fill menu gaps.
- Other schools. The FoodPro and Nutrislice menu systems behind UMass's data run dining at hundreds of colleges, so adding a campus is a new scraper, not a rebuild.
