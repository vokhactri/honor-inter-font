# Honor Inter font

A font theme for Honor phones running MagicOS that sets [Inter](https://rsms.me/inter/) as the system font, with every weight from 100 to 900 and full Vietnamese.

The theme replaces the system font everywhere, including the system monospace font. Code blocks in apps such as Telegram and Paseo then lose their column alignment. Apps that bundle their own fonts are not affected. Choose Default in Themes > Fonts to go back to HONOR Sans.

For dark icon themes, see [honor-dark-theme](https://github.com/vokhactri/honor-dark-theme).

## Install

1. Download `Inter-Font-Honor.hnt` from [Releases](../../releases).
2. Move it to the `Honor/Themes` folder in the phone's internal storage.
3. Restart the phone. The Themes app looks for new files in `Honor/Themes` only at boot, not when you reopen it.
4. Open Themes > Fonts and apply Inter.

The Themes app caches the font card. To see new preview images after an update, apply Default, delete Inter in the app, put the new file in `Honor/Themes` and restart.

## Build

You need [uv](https://docs.astral.sh/uv/). It runs on macOS and Linux.

```sh
uv run -m theme.build    # writes dist/Inter-Font-Honor.hnt
```

Format and lint with ruff before committing:

```sh
uv run ruff format
uv run ruff check
```

## Release

1. Build, then try the theme on the phone.

   ```sh
   uv run -m theme.build
   adb push dist/Inter-Font-Honor.hnt /sdcard/Honor/Themes/
   adb reboot
   ```

2. Bump the version: `patch` for fixes, `minor` for a new Inter release, `major` for a new font.

   ```sh
   uv version --bump minor    # updates pyproject.toml and uv.lock
   ```

3. Commit, tag and push. The tag comes from the version, so the two always match.

   ```sh
   V=v$(uv version --short)
   git commit -am "release: $V"
   git tag "$V" && git push origin main "$V"
   ```

GitHub Actions then builds the theme on Linux and publishes it as a release with generated notes. To check a CI build without releasing, run the Release workflow by hand and download the `font` artifact.

## How it works

A font theme is a `.hnt` (an uncompressed zip) with `<type>font</type>` in `description.xml`. When you apply it, MagicOS copies its `fonts/` folder to `/data/themes/0/fonts` and loads the first of these it finds:

1. `online_variable_fonts.xml`: a `fonts.xml`-style family with one `<font>` per weight, here each a `wght` instance of `InterVariable.ttf`. Bold is real bold, and the font weight slider in Settings keeps working.
2. `DroidSansChinese.ttf`: a single file. Bold is faked and the weight slider is off. It is kept as a fallback.

The theme font comes before HONOR Sans and every other system font for each character it covers, which is why the monospace font changes too. Only one family can be set, so there is no way to keep a separate monospace font, and no way to switch Inter's optical size (`opsz`) by text size: it stays at 14, the text cut.

The Themes app also drops any theme without both `preview/` and `icons` entries, so the theme carries an empty `icons/` folder. The cards in Themes > Fonts (`fonts/pic_font_default*.jpg`) and the detail page (`preview/preview_fonts_0_50*.png`) copy the layout of Honor's built-in Android font theme.

## Layout

```
theme/build.py   packs the theme and draws its preview cards
data/inter/      Inter 4.1 (SIL OFL): InterVariable.ttf, and Inter-Regular.ttf for the fallback
```

## Credits

Inter is by Rasmus Andersson and the Inter Project Authors, under the SIL Open Font License (`data/inter/LICENSE.txt`).
