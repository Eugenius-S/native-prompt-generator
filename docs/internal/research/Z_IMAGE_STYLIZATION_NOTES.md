# Z-Image Stylization Notes

Source:
- `Face Swappper Ads/z_image.md` (internal notes)

## Main Takeaways

- Z-Image understands long natural-language photo prompts better than tag soup.
- The model responds better to photo concepts than abstract art labels.
- Word order matters: first photo treatment / light / camera vibe, then subject / outfit / scene details.
- By default, the model tends toward an overly polished glossy stock-commercial look.
- For dark / moody results, do not just write `dark`; specify concrete lighting mechanics:
  - `low-key lighting`
  - `single hard light`
  - `deep shadows`
  - `underexposed room`
  - `harsh direct flash`
  - `black background`
  - `high contrast`
- Complex camera-angle commands are not the model's strong suit.
- For a more grounded result, specify a medium/context:
  - `smartphone photo`
  - `point-and-shoot snapshot`
  - `35mm film`
  - `Polaroid instant photo`
  - `DSLR portrait`
- Community experience suggests that style concepts work better than `in the style of ...`.

## Native Z-Image-Friendly Directions

The most natural directions for the model are:

- clean commercial fashion editorial
- beauty / editorial portrait
- luxury beauty portrait
- candid smartphone / mirror selfie / social snapshot
- 35mm analog film portrait
- point-and-shoot snapshot
- Polaroid instant photo
- low-key dramatic studio portrait
- direct-flash nightlife photo
- cinematic movie-poster realism
- professional product / food photography

## Things That Usually Work Worse

- abstract art-style labels without photo context
- just `dark / moody` without specifics about light
- overly complex camera-angle commands
- short tag prompts instead of a structured description

## Implications For Prompt Generator

The new generation layer should be `photo treatment`, not `art style`.

By `photo treatment`, I mean a bundle of:
- capture language
- lighting family
- camera / medium vibe
- color grade
- finish / processing
- compatibility constraints with scene/style

## Recommended Default Random Mix

- `40%` clean polished professional / stock-commercial
- `60%` stylized photo treatments

Recommended stylized pool:
- candid phone / snapshot
- analog / 35mm / point-and-shoot
- low-key dramatic portrait
- direct-flash nightlife
- studio seamless background
- cinematic poster realism

## Practical Rule

Think not as a `style name`, but as:

`what is being shot + what light + what camera vibe + what color grade + what finish`

That is roughly the order in which it should be rendered in the prompt.
