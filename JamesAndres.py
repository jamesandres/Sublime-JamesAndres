import sublime, sublime_plugin, re, subprocess, math

# Tests 1 10 101 123 999 0x1c

class JaMathDecHexCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    sel = self.view.sel()

    # replace all regions with math alteration
    for region in sel:
      word = self.view.word(region)
      text = self.view.substr(word)

      if text.isdecimal():
        self.view.replace(edit, region, "0x%x" % int(text))

class JaMathHexDecCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    sel = self.view.sel()

    # replace all regions with math alteration
    for region in sel:
      word = self.view.word(region)
      text = self.view.substr(word)

      if re.findall('^0x[a-f0-9]+$', text):
        self.view.replace(edit, region, str(int(text, 16)))

class JaPhpUnserializeCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    sel = self.view.sel()

    for region in sel:
      word = self.view.word(region)
      text = self.view.substr(word)

      cleanText = text.replace("'", "\\'")
      unserialized = subprocess.Popen(["php",
                                       "-r",
                                       "ini_set('display_errors', 1); var_export(unserialize('" + cleanText + "'));"],
                                      stdout = subprocess.PIPE).communicate()[0]

      if unserialized != "false" or text == 'b:0;':
        self.view.replace(edit, region, unserialized)
      else:
        pass

class JaColumnizerCommand(sublime_plugin.TextCommand):
  def run(self, edit, columns):
    sel = self.view.sel()

    if columns == "fit":
      width = int(self.view.settings().get("rulers")[0])
    else:
      width = 0

    for region in sel:
      word = self.view.word(region)
      text = self.view.substr(word)

      # 3. Fit them 2 or 3 cols, needs to be configurable

      lines = text.split("\n")
      lines = map(lambda s: s.strip(), lines)

      # Find the longest line, add 1 to it for padding
      longest = 0
      for line in lines:
        length = len(line) + 1
        longest = max(longest, length)

      # Try an calculate the fit of the longest line into the 
      if columns == "fit":
        columns = math.floor(width / longest)

      columns = int(columns)

      # Never try to columnize for a non-positive number of columns!
      if columns > 0:
        # The printf format string for each column, eg: "%-30s"
        fmt = "%-" + str(longest) + "s"
        rows = []

        while True: # Sorta do-while loop
          row = []
          for i in range(columns):
            row.append(self.unshiftLine(lines))

          rows.append(((fmt * columns) % tuple(row)).rstrip())

          if len(lines) <= 0:
            break

        self.view.replace(edit, region, "\n".join(rows))

  def unshiftLine(self, lines):
    if len(lines) <= 0:
      return ''
    else:
      return lines.pop(0)

