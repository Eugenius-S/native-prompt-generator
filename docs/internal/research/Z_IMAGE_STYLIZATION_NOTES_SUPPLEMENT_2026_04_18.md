# Z-Image Stylization Notes Supplement

Source:
- `C:\Users\jiraf\Desktop\z_image_project_stylization_recommendations.md`

New useful points worth keeping for future stylization work:

- Add `composition` as an explicit stylization axis alongside light / camera / grade / finish.
- Grounded realism prompts benefit from words like:
  - `ordinary`
  - `everyday`
  - `unpolished realism`
  - `handheld`
  - `ambient indoor light`
- The following lanes are worth treating as separate practical buckets, not just synonyms:
  - `mirror selfie`
  - `casual indoor selfie`
  - `disposable camera look`
  - `documentary film still`
  - `vintage flash photography`
  - `advertising poster realism`
  - `magazine-cover portrait`
  - `branded campaign image`
  - `product hero shot`
  - `professional food photography`
- Recommended style-template order can be thought of as:
  - shot type
  - light
  - camera / medium
  - color / mood
  - scene context
  - key details
- Important anti-patterns to avoid in the generator:
  - mixing `natural candid` with `luxury polished commercial` in the same style lead
  - stacking too many genre directions at once
  - relying on empty quality words without photo meaning
  - trying to solve weak scene prompting only through negative prompts

Potential future branch:

- a separate commercial/product stylization branch for:
  - beauty / cosmetics campaign
  - product still life
  - premium food / restaurant ad
