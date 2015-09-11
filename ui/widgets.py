import urwid as ur

class WidgetFactory:
	def __init__(self, separator=': '):
		self.separator = separator
	
	def get_widget(self, param):
		wtype = param['type']
		if wtype == 'string':
			return FreeTextParamWidget(param, self.separator)
		elif wtype == 'boolean':
			return BooleanParamWidget(param)
		elif wtype == 'singleselect':
			return SingleChoiceParamWidget(param)
		elif wtype == 'multiselect':
			return MultiChoiceParamWidget(param)
		else:
			raise ValueError("Unrecognized parameter type %s" % wtype)

class ParamWidget:
	def reset(self):
		raise NotImplementedError
	def get_value(self):
		raise NotImplementedError

class FreeTextParamWidget(ParamWidget, ur.Edit):
	def __init__(self, param, separator=': '):
		super(FreeTextParamWidget, self).__init__('%s%s' % (param['label'], separator), '')
	def reset(self):
		self.set_edit_text('')
	def get_value(self):
		return self.get_edit_text()

class BooleanParamWidget(ParamWidget, ur.CheckBox):
	def __init__(self, param):
		self.default = param.get('default', False)
		super(BooleanParamWidget, self).__init__(param['label'], param['default'])
	def reset(self):
		self.set_state(self.default)
	def get_value(self):
		if self.get_state():
			return '' 
		else:
			return None

class ChoiceParamWidget(ParamWidget, ur.Pile):
	def __init__(self, param):
		self.length = len(param['options'])
		self.selection = param.get('default')
		self.default = param.get('default')
		widget_list = [ur.Text(param['label'])] + self._get_option_subwidgets(param)
		super(ChoiceParamWidget, self).__init__(widget_list, self.default)

	def _get_option_subwidgets(self, param):
		raise NotImplementedError

	def __len__(self):
		return self.length

	def reset(self):
		if self.selection != None:
			i = 1
			while i < len(self):
				self[i].set_state(False)
				i += 1
			self.selection = self.default

class SingleChoiceParamWidget(ChoiceParamWidget):
	def _get_option_subwidgets(self, param):
		self.group = []
		return [ur.RadioButton(self.group, option, False, self._set_value) for option in param['options']]

	def get_value(self):
		return self.selection

	def _set_value(self, button, state):
		if state:
			self.selection = button.label

class MultiChoiceParamWidget(ChoiceParamWidget):
	def _get_option_subwidgets(self, param):
		self.delimiter = param['delimiter']
		return [ur.CheckBox(option, False, False, self._set_value) for option in param['options']]

	def get_value(self):
		if self.selection:
			return self.delimiter.join(self.selection)
		else:
			return None

	def _set_value(self, button, state):
		if not self.selection:
			self.selection = []
		if state:
			self.selection.append(button.label)
		else:
			try:
				self.selection.remove(button.label)
			except ValueError:
				pass

