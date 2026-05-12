# Line-Bank Troubleshooting

## Safe Starter Rule

- comment-only `1_3.md`, `4_5.md`, and `6_8.md` files are safe
- they do not create live records until you add at least one non-comment line

## If Your New Line Does Not Show Up

Check these in order:

1. use the right gender folder: `women/` or `men/`
2. use the right domain folder: `poses/`, `outfits/`, or `expressions/`
3. use the right bucket filename: `1_3.md`, `4_5.md`, or `6_8.md`
4. make sure the line does not start with `#`
5. make sure the line is not blank
6. make sure the line is not too short
7. make sure the line is under the character cap

## Character Caps

- `poses`: `140`
- `expressions`: `120`
- `outfits`: `160`

## Common Mistakes

- putting a men line under `women/` and expecting it in men mode
- putting a couples-style phrase into men or women banks and expecting couples output to use it
- adding multiple ideas in one long sentence instead of one atomic item
- pasting whole prompt paragraphs instead of one pose, one outfit, or one expression
- creating a typo path like `women/pose/4_5.md` instead of `women/poses/4_5.md`

## Good Line Shapes

Use short, atomic lines.

Good `poses` shape:

- one clear body stance
- one camera-facing attitude or movement beat

Good `outfits` shape:

- one concise look
- no giant styling paragraph

Good `expressions` shape:

- one face expression
- short and readable

## If Output Starts Feeling Bloated

Do this:

1. shorten the line
2. remove extra clauses
3. keep only the strongest visual idea
4. split different ideas into separate lines instead of one long line

## If You Want Zero Effect Again

Do one of these:

1. delete the live text lines and leave only `#` comments
2. clear the file completely
3. move the experimental lines out of the live folder
