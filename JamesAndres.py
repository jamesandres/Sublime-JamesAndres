import sublime, sublime_plugin, re, subprocess

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
