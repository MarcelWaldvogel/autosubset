# autosubset – Automatically subset a font based on actual text

`autosubset` creates a subset font exactly for the set of characters that you
actually use.

## Usage

Just pipe the text into `autosubset` and specify the font.

Assuming all your text is in the HTML files in the current directory:
```sh
html2text *.html | autosubset.py MyFont.woff2
```
`autosubset` analyzes the content, extracts the characters used and uses
[`pyftsubst`](https://fonttools.readthedocs.io/en/latest/subset/) from
[fonttools](https://github.com/fonttools/fonttools) to create a matching
subset.

After that, just add lines like the following to your web site:

* **HTML**: Preload the font for faster availability.
  ```html
  <link rel="preload" href="MyFont.subset.woff2" as="font" type="font/woff2">
  ```
* **CSS**: Define and use the font.
  ```css
  @font-face {
    font-family: "My Font";
    src: local("Tenor Sans"), url("MyFont.subset.woff2") format("woff2");
    font-display: fallback;
  }
  @body {
    font-family: "My Font", "System Fallback Font", sans;
  }
  ```

Whenever you change your text, make sure to rerun `autosubst`. This ensures
that the browser does not need to substitute characters from the fallback
fonts.
