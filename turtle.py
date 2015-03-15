#!/usr/bin/env python

import subprocess
import sys
import urwid as ur
import yaml
from ui.widgets import *

def command_form_from_file(filename):
	f = open(filename)
	raw = yaml.safe_load(f)
	f.close()
	command = raw['command']
	params = raw['params']
	form = CommandForm(command, params)
	return form

class CommandForm:
	def __init__(self, command, params=[], env={}, user=''):
		self.command = command
		self.params = params
		self.env = env
		self.user = user
	
	def __len__(self):
		return len(self.params)

	def __str__(self):
		return self.command + ' ' +  ' '.join(['%s %s' % (v['flag'], v['value']) for v in self.params if v.has_key('value')])
	
	def set_values(self, pile):
		i = 0
		while i < len(self):
			v = pile[i].get_value()
			if v != None:
				self.params[i]['value'] = v
			elif self.params[i].has_key('value'):
				del(self.params[i]['value'])
			i += 1

class FormListBox(ur.ListBox):
	def __init__(self, form, separator=': '):
		self.form = form
		self.separator = separator
		self.widget_factory = WidgetFactory(separator)
		body = ur.SimpleFocusListWalker([
			ur.Pile(self._get_widgets()),
			ur.AttrWrap(ur.Text(''), 'command'),
			ur.Columns([
				ur.AttrWrap(ur.Button('Execute', self.execute), 'execute'),
				ur.AttrWrap(ur.Button('Reset', self.reset), 'reset'),
				ur.AttrWrap(ur.Button('Exit', self.exit), 'exit')
				]),
			ur.AttrWrap(ur.Text(''), 'output')
			])
		super(FormListBox, self).__init__(body)
		self.update()

	def _get_widgets(self):
		return [self.widget_factory.get_widget(param) for param in self.form.params]

	def exit(self, *args):
		self.update()
		raise ur.ExitMainLoop()
	
	def execute(self, button):
		self.update()
		output = subprocess.Popen(str(self.form), shell=True, stdout=subprocess.PIPE).stdout.read()
		self.body[3].set_text(output)

	def reset(self, button):
		[self.body[0][i].reset() for i in range(0, len(self.form))]
		self.body[3].set_text('')
		self.update()

	def update(self):
		self.form.set_values(self.body[0])
		self.body[1].set_text(str(self.form))

	def keypress(self, size, key):
		key = super(FormListBox, self).keypress(size, key)
		if self.focus_position == 0:
			if key == 'enter':
				self.update()
				if self.focus.focus_position < len(self.form) - 1:
					self.focus.focus_position += 1
				else:
					self.focus_position += 2
			elif key == 'ctrl d':
				self.exit()
			else:
				return key
		else: # TODO: Handle ctrl d outside of form
			return key

def __main__():
	if len(sys.argv) != 2:
		raise ValueError("Exactly one command configuration file must be specified")
	filename = sys.argv[1]
	form = command_form_from_file(filename)
	palette = [
			('command', 'black,bold', 'yellow'),
			('output', 'black,bold', 'dark green'),
			('execute', 'white,bold', 'dark red'),
			('exit', 'white,bold', 'black'),
			('reset', 'white,bold', 'dark blue')
			]
	ur.MainLoop(FormListBox(form), palette).run()
	print form

if __name__ == '__main__':
	__main__()

