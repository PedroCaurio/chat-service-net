# FEITO COM GEMINI
#
#       TRABALHO EM ANDAMENTO - MTA IA AINDA
#
# client/GUI/chat_screen.py
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QListWidget, 
    QTextEdit, QLineEdit, QPushButton, QListWidgetItem,
    QLabel, QFrame, QApplication, QStyle
)
from PyQt6.QtCore import pyqtSignal, pyqtSlot, Qt, QSize, QTime
from PyQt6.QtGui import QFont, QIcon

# ===================================================================
# 1. CLASSE DE ESTILO (Para alterar as cores)
# ===================================================================
class ChatStyle:
    """ Altere as cores da sua aplicação aqui """
    
    # Cores de Fundo
    BG_APP = "#FDFDFD"          # Fundo geral
    BG_LIST = "#F6F5FA"         # Fundo da lista de contatos (lilás claro)
    BG_CHAT = "#FFFFFF"         # Fundo da área de chat
    BG_INPUT = "#838383"        # Fundo da área de digitação

    # Cores dos Itens da Lista
    ITEM_SELECTED_BG = "#D9FDD3" # Item selecionado (verde claro)
    ITEM_DEFAULT_BG = "transparent"
    
    # Cores das Bolhas de Chat
    BUBBLE_SENT_BG = "#D9FDD3"   # Bolha enviada (verde)
    BUBBLE_SENT_TEXT = "#000000"
    
    BUBBLE_RECEIVED_BG = "#F1F0F0" # Bolha recebida (cinza)
    BUBBLE_RECEIVED_TEXT = "#000000"

    # Cores de Texto
    TEXT_PRIMARY = "#000000"    # Nomes dos contatos
    TEXT_SECONDARY = "#000000"  # Preview da mensagem
    TEXT_TIMESTAMP = "#999999"  # Timestamp (09:10)

    # Notificação
    NOTIFICATION_BG = "#4CAF50" # Círculo da notificação (verde)
    NOTIFICATION_TEXT = "#FFFFFF"

    # Bordas
    BORDER_COLOR = "#EAEAEA"

# ===================================================================
# 2. WIDGET CUSTOMIZADO PARA A LISTA DE CONTATOS
# ===================================================================
class ContactItemWidget(QFrame):
    """
    Widget customizado para cada item da lista de contatos.
    Mostra Nome, Última Mensagem e Notificações.
    """
    def __init__(self, name, last_message, notification_count=0):
        super().__init__()
        self.name = name
        
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Layout Esquerdo (Nome e Mensagem)
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        self.name_label = QLabel(name)
        font = self.name_label.font()
        font.setBold(True)
        font.setPointSize(11)
        self.name_label.setFont(font)
        self.name_label.setStyleSheet(f"color: {ChatStyle.TEXT_PRIMARY};")
        
        self.message_label = QLabel(last_message)
        font = self.message_label.font()
        font.setPointSize(9)
        self.message_label.setFont(font)
        self.message_label.setStyleSheet(f"color: {ChatStyle.TEXT_SECONDARY};")
        
        text_layout.addWidget(self.name_label)
        text_layout.addWidget(self.message_label)
        
        # Layout Direito (Notificação)
        self.notification_label = QLabel()
        self.notification_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        main_layout.addLayout(text_layout)
        main_layout.addWidget(self.notification_label)
        main_layout.setStretch(0, 1) # Layout de texto ocupa mais espaço
        
        self.setLayout(main_layout)
        self.set_notifications(notification_count)
        self.set_selected(False) # Começa como não selecionado

    def set_notifications(self, count):
        if count > 0:
            self.notification_label.setText(str(count))
            self.notification_label.setStyleSheet(f"""
                background-color: {ChatStyle.NOTIFICATION_BG};
                color: {ChatStyle.NOTIFICATION_TEXT};
                border-radius: 10px;
                padding: 1px 5px;
                min-width: 10px;
                max-height: 18px;
                font-size: 9pt;
                font-weight: bold;
            """)
        else:
            self.notification_label.setText("")
            self.notification_label.setStyleSheet("background-color: transparent;")

    def set_selected(self, selected):
        """ Atualiza o visual do item para refletir a seleção """
        if selected:
            self.setStyleSheet(f"background-color: {ChatStyle.ITEM_SELECTED_BG}; border-radius: 8px;")
        else:
            self.setStyleSheet(f"background-color: {ChatStyle.ITEM_DEFAULT_BG}; border-radius: 8px;")

# ===================================================================
# 3. TELA DE CHAT PRINCIPAL (Atualizada)
# ===================================================================
class ChatScreen(QWidget):
    """
    Tela principal do chat. Mostra contatos/grupos e a conversa.
    """
    
    # Sinais para o ClientService
    private_message_sended = pyqtSignal(str, str) # recipient, message
    group_message_sended = pyqtSignal(str, str)   # group_id, message
    general_message_sended = pyqtSignal(str)      # message
    create_group = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.user_id = None
        self.current_chat_target = None # Guarda o alvo atual
        self.chat_widgets = {} # Mapeia ID -> ContactItemWidget

        # Layout principal (Horizontal: contatos | chat)
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- Coluna da Esquerda (Contatos e Grupos) ---
        left_frame = QFrame()
        left_frame.setStyleSheet(f"background-color: {ChatStyle.BG_LIST};")
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(10, 10, 10, 10)
        left_layout.setSpacing(10)
        
        commands_title = QLabel("Comandos")
        font = commands_title.font()
        font.setPointSize(16)
        font.setBold(True)
        commands_title.setFont(font)
        
        self.commands_list = QVBoxLayout()
        self.create_group_btn = QPushButton("Criar grupo")
        self.commands_list.addWidget(self.create_group_btn)

        list_title = QLabel("Mensagens")
        font = list_title.font()
        font.setPointSize(16)
        font.setBold(True)
        list_title.setFont(font)
        
        self.contact_list = QListWidget()
        self.contact_list.setStyleSheet(f"""
            QListWidget {{
                border: none;
                background-color: transparent;
                outline: 0;
            }}
            QListWidget::item {{
                padding: 4px 0px;
            }}
            QListWidget::item:selected {{
                background-color: transparent;
            }}
        """)
        self.contact_list.setSpacing(5)
        
        left_layout.addWidget(commands_title)
        left_layout.addWidget(self.create_group_btn)
        left_layout.addWidget(list_title)
        left_layout.addWidget(self.contact_list)

        # --- Coluna da Direita (Chat) ---
        right_frame = QFrame()
        right_frame.setStyleSheet(f"background-color: {ChatStyle.BG_CHAT};")
        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        
        # Título do Chat (ex: "Arthur")
        self.chat_title_label = QLabel("Selecione um chat")
        font = self.chat_title_label.font()
        font.setPointSize(12)
        font.setBold(True)
        self.chat_title_label.setFont(font)
        self.chat_title_label.setStyleSheet(f"""
            padding: 15px;
            border-bottom: 1px solid {ChatStyle.BORDER_COLOR};
            color: {ChatStyle.TEXT_PRIMARY};
        """)
        
        # Área de exibição do chat
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet(f"""
            background-color: {ChatStyle.BG_CHAT};
            border: none;
            padding: 10px;
            color: {ChatStyle.TEXT_PRIMARY};
        """)

        # Área de Input
        input_frame = QFrame()
        input_frame.setStyleSheet(f"""
            background-color: {ChatStyle.BG_INPUT};
            border-top: 1px solid {ChatStyle.BORDER_COLOR};
        """)
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(10, 10, 10, 10)

        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Digite sua mensagem...")
        self.message_input.setStyleSheet(f"""
            border: 1px solid {ChatStyle.BORDER_COLOR};
            border-radius: 15px;
            padding: 8px 12px;
            font-size: 10pt;
        """)
        
        self.send_button = QPushButton()
        # Usar um ícone padrão do PyQt
        icon = QApplication.style().standardIcon(QStyle.StandardPixmap.SP_ArrowRight)
        self.send_button.setIcon(icon)
        self.send_button.setFixedSize(32, 32)
        self.send_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {ChatStyle.NOTIFICATION_BG};
                color: white;
                border-radius: 16px;
            }}
            QPushButton:hover {{
                background-color: #45a049;
            }}
        """)
        
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)
        
        right_layout.addWidget(self.chat_title_label)
        right_layout.addWidget(self.chat_display, 1) # 1 = stretch factor
        right_layout.addWidget(input_frame)

        main_layout.addWidget(left_frame, 30) # 30% do espaço
        main_layout.addWidget(right_frame, 70) # 70% do espaço
        self.setLayout(main_layout)

        # Conexões internas
        self.create_group_btn.clicked.connect(self.on_create_group_clicked)
        self.send_button.clicked.connect(self.on_send_clicked)
        self.message_input.returnPressed.connect(self.on_send_clicked)
        self.contact_list.currentItemChanged.connect(self.on_chat_selected)
        
    def _add_chat_item(self, data, last_message, count=0):
        """ Helper para adicionar um item customizado à lista """
        item_id = data["id"]
        item_type = data["type"]
        
        # O nome pode ser o ID ou um nome mais amigável
        name = "Geral" if item_id == "General" else item_id
        
        item = QListWidgetItem(self.contact_list)
        widget = ContactItemWidget(name, last_message, count)
        
        # Guarda os dados no item
        data["widget"] = widget # Referência para o widget
        item.setData(Qt.ItemDataRole.UserRole, data)
        
        # Adiciona o item e widget customizado
        item.setSizeHint(widget.sizeHint())
        self.contact_list.addItem(item)
        self.contact_list.setItemWidget(item, widget)
        
        self.chat_widgets[item_id] = widget
        return item

    def _format_bubble(self, sender, message, timestamp, is_sent):
        """ Formata uma string HTML para a bolha de chat """
        
        if is_sent:
            align = "right"
            bg_color = ChatStyle.BUBBLE_SENT_BG
            text_color = ChatStyle.BUBBLE_SENT_TEXT
            sender_html = "" # Não mostramos o sender para nós mesmos
        else:
            align = "left"
            bg_color = ChatStyle.BUBBLE_RECEIVED_BG
            text_color = ChatStyle.BUBBLE_RECEIVED_TEXT
            # Mostrar o sender se for chat em grupo ou geral
            target_type = self.current_chat_target.get("type", "private")
            if target_type != "private":
                sender_html = f"<span style='font-size: 9pt; color: {ChatStyle.TEXT_SECONDARY}; font-weight: bold;'>{sender}</span><br>"
            else:
                sender_html = ""

        bubble_style = f"""
            background-color: {bg_color};
            color: {text_color};
            border-radius: 10px;
            padding: 8px 12px;
            max-width: 60%;
            display: inline-block;
        """
        
        timestamp_style = f"font-size: 8pt; color: {ChatStyle.TEXT_TIMESTAMP};"

        html = f"""
        <div align='{align}'>
            <div style='{bubble_style}'>
                {sender_html}
                <span style='font-size: 10pt;'>{message.replace("\\n", "<br>")}</span>
                <br>
                <span style='{timestamp_style}; text-align: right; display: block;'>{timestamp}</span>
            </div>
            <div style='height: 5px;'></div>
        </div>
        """
        return html

    def on_create_group_clicked(self):
        self.create_group.emit()
    def on_send_clicked(self):
        """
        Chamado para enviar uma mensagem.
        Emite o sinal e adiciona a bolha de "enviado" localmente.
        """
        message = self.message_input.text().strip()
        if not message or not self.current_chat_target:
            return

        target_type = self.current_chat_target.get("type")
        target_id = self.current_chat_target.get("id")

        # 1. Adiciona a bolha localmente
        timestamp = QTime.currentTime().toString("HH:mm")
        html = self._format_bubble(self.user_id, message, timestamp, is_sent=True)
        self.chat_display.append(html)
        self.message_input.clear()
        
        # 2. Atualiza o preview na lista
        self.current_chat_target["widget"].message_label.setText(f"Eu: {message}")

        # 3. Emite o sinal para o ClientService
        if target_type == "general":
            self.general_message_sended.emit(message)
        elif target_type == "private":
            self.private_message_sended.emit(target_id, message)
        elif target_type == "group":
            self.group_message_sended.emit(target_id, message)

    def on_chat_selected(self, current_item: QListWidgetItem):
        """Atualiza o alvo do chat e o visual da lista."""
        if not current_item:
            return
        
        self.current_chat_target = current_item.data(Qt.ItemDataRole.UserRole)
        target_id = self.current_chat_target['id']
        
        # Atualiza o título do chat
        self.chat_title_label.setText("Geral" if target_id == "General" else target_id)
        
        # Limpa o chat e reseta notificações
        self.chat_display.clear()
        self.current_chat_target["widget"].set_notifications(0) 
        
        # Atualiza o visual de seleção na lista
        for i in range(self.contact_list.count()):
            item = self.contact_list.item(i)
            widget = self.contact_list.itemWidget(item)
            if item == current_item:
                widget.set_selected(True)
            else:
                widget.set_selected(False)


    # --- Slots para o ClientService ---

    @pyqtSlot(str, dict)
    def load_user_data(self, user_id, users):
        """ Configura a tela de chat após o login. """
        self.user_id = user_id
        self.contact_list.clear()
        self.chat_widgets.clear()
        
        for user in users:
            if user != user_id:
                self._add_chat_item(
                    {
                    "type": "private", 
                    "id": user,
                    },
                    users[user] # ultima mensagem
                )
        
        # Adiciona o chat "Geral" como placeholder
        item_geral = self._add_chat_item(
            {"type": "general", "id": "General"}, 
            "Chat com todos os usuários"
        )
        '''
        # Adiciona contatos fixos (exemplo)
        self._add_chat_item(
            {"type": "private", "id": "fulano"},
            "Clique para conversar", 2
        )
        self._add_chat_item(
            {"type": "private", "id": "ciclano"},
            "Ok, obrigado!", 0
        )
        self._add_chat_item(
            {"type": "group", "id": "Faculdade"},
            "Trabalho amanhã?", 5
        )
        
        # Seleciona o "Geral" por padrão
        self.contact_list.setCurrentItem(item_geral)
        '''


    @pyqtSlot(list)
    def update_user_list(self, users: list):
        """
        (Idealmente) Recebe a lista de usuários do servidor e atualiza
        a QListWidget dinamicamente.
        """
        # Esta lógica precisa ser implementada
        # Você pode usar self._add_chat_item() para adicionar novos usuários
        pass 

    def _add_message(self, target_id, sender, message, is_group=False):
        """ Lógica central para adicionar uma mensagem recebida """
        timestamp = QTime.currentTime().toString("HH:mm")
        
        # Atualiza o preview na lista da esquerda
        if target_id in self.chat_widgets:
            widget = self.chat_widgets[target_id]
            widget.message_label.setText(f"{sender}: {message}")
        
        # Se o chat estiver selecionado, adiciona a bolha
        if self.current_chat_target and self.current_chat_target.get("id") == target_id:
            html = self._format_bubble(sender, message, timestamp, is_sent=False)
            self.chat_display.append(html)
        else:
            # Se não, incrementa a notificação
            if target_id in self.chat_widgets:
                # (Lógica para incrementar notificação - por enquanto só seta para 1)
                widget.set_notifications(1) # Implementação simples

    @pyqtSlot(str, str)
    def add_private_message(self, sender, message):
        """ Adiciona mensagem privada (o ID do alvo é o sender) """
        print("\n\nmensagem privada: ", message)
        self._add_message(target_id=sender, sender=sender, message=message)

    @pyqtSlot(str, str, str)
    def add_group_message(self, group_id, sender, message):
        """ Adiciona mensagem de grupo """
        self._add_message(target_id=group_id, sender=sender, message=message, is_group=True)

    @pyqtSlot(str, str)
    def add_general_message(self, sender, message):
        """ Adiciona mensagem geral """
        self._add_message(target_id="General", sender=sender, message=message, is_group=True)