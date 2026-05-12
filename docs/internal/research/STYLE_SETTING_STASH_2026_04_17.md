# Style And Setting Stash 2026-04-17

Status:
- not connected to live
- this is raw material for the next small imports into `drafts/setting_engine` and possibly new style/routing banks

Source:
- `C:\Users\jiraf\Documents\ComfyUI\!agent_instructions\03_LIBRARIES\beautiful_life_interiors_social_2026.md`
- `C:\Users\jiraf\Documents\ComfyUI\!agent_instructions\03_LIBRARIES\prompt_library_main.md`
- `C:\Users\jiraf\Documents\ComfyUI\!agent_instructions\03_LIBRARIES\prompt_library_extracted_refs.md`

## Useful system

It is better to add not "another random pretty interior", but packages like:
- `style family`
- `setting family`
- `props`
- `light behavior`
- `pose logic`

So not just `bar`, but:
- `slow luxury nightlife`
- `private members club bar`
- `backlit bottles, ribbed oak, leather banquette`
- `low amber lamp pools`
- `seated booth / standing close / glass in hand`

## Candidate style families

- `quiet_luxury_day`
  - polished, expensive, calm, airy, daylight, marble/wood/brass
- `hotelized_life`
  - suite, breakfast nook, room service, robe-and-vanity, private comfort
- `slow_luxury_night`
  - wine lounge, members club, amber lamps, leather, shadow, intimate but not trashy
- `grooming_glam`
  - vanity, powder room, dressing suite, mirror wall, flattering side light
- `wellness_restorative`
  - spa lounge, plunge room, steam shower, towels, tea service, quiet reset
- `collected_richness`
  - art books, objects, layered upholstery, quiet expensive clutter
- `architectural_soft_power`
  - stair hall, gallery corridor, tall glass, hard lines, soft body language
- `transport_polish`
  - train compartment, airport lounge, yacht cabin, travel but expensive and composed

## Candidate setting families

### Luxury / Home / Quiet social

- sunlit penthouse living room
- quiet penthouse breakfast nook
- sculptural stair hall
- understated townhouse salon
- old-money apartment library
- glamorous vanity corner

### Hotel / Hospitality

- luxury hotel suite sitting area
- hybrid hotel lobby lounge
- suite hallway with lacquer console
- rooftop hotel conservatory
- boutique hotel corridor
- room-service breakfast table by a panoramic window

### Dressing / Beauty / Prep

- double-height walk-in closet
- mirrored dressing room
- boutique changing suite
- old Hollywood makeup room
- bridal-style suite prep room
- marble beauty counter

### Spa / Wellness

- adults-only spa lounge
- steam shower chamber
- spa plunge room
- recovery lounge
- resort massage suite
- gym lounge with hydration bar

### Night / Social / Club

- private members club bar
- wine lounge with ribbed oak
- lounge booth in a luxury cocktail bar
- cigar-style library bar
- art deco disco lobby
- after-party powder room

## What is worth carrying forward next

If we take the next small batch, I would pull:
- `sunlit_penthouse_living_room`
- `double_height_walkin_closet`
- `hybrid_hotel_lobby_lounge`
- `private_members_club_bar`
- `marble_primary_bathroom`
- `rooftop_hotel_conservatory_palms`
- `adults_only_spa_lounge`
- `wine_lounge_ribbed_oak`

## How to wire this cheaply later

1. first one tiny `drafts/setting_engine/*.json`
2. then one tiny `drafts/styling/*.json` if a special outfit/material/color packet is needed
3. only after validation promote the piece into core

Do not dump a large bank in one go.
