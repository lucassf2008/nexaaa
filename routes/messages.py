from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, g
from models import db, User, Message, Notification
from auth import login_required

messages_bp = Blueprint('messages', __name__)

@messages_bp.route('/mensagens')
@login_required
def inbox():
    user = g.current_user
    active_user_id = request.args.get('user_id', type=int)

    # Buscar todas as mensagens envolvendo o usuário atual
    all_msgs = Message.query.filter(
        (Message.sender_id == user.id) | (Message.receiver_id == user.id)
    ).order_by(Message.created_at.asc()).all()

    # Agrupar conversas por interlocutor
    conversations = {}
    for msg in all_msgs:
        other_user = msg.receiver if msg.sender_id == user.id else msg.sender
        if other_user.id not in conversations:
            conversations[other_user.id] = {
                'user': other_user,
                'last_message': msg,
                'unread_count': 0,
                'messages': []
            }
        conversations[other_user.id]['messages'].append(msg)
        conversations[other_user.id]['last_message'] = msg
        if not msg.is_read and msg.receiver_id == user.id:
            conversations[other_user.id]['unread_count'] += 1

    # Ordenar conversas pela última mensagem
    conv_list = sorted(
        conversations.values(),
        key=lambda c: c['last_message'].created_at,
        reverse=True
    )

    # Se um usuário específico foi selecionado
    active_chat = None
    if active_user_id:
        if active_user_id in conversations:
            active_chat = conversations[active_user_id]
        else:
            # Nova conversa iniciada
            target_user = db.session.get(User, active_user_id)
            if target_user and target_user.id != user.id:
                active_chat = {
                    'user': target_user,
                    'last_message': None,
                    'unread_count': 0,
                    'messages': []
                }
                conv_list.insert(0, active_chat)
    elif conv_list:
        active_chat = conv_list[0]

    # Marcar mensagens do chat ativo como lidas
    if active_chat and active_chat['user']:
        unread_in_active = Message.query.filter_by(
            sender_id=active_chat['user'].id,
            receiver_id=user.id,
            is_read=False
        ).all()
        for m in unread_in_active:
            m.is_read = True
        db.session.commit()

    return render_template(
        'messages.html',
        conversations=conv_list,
        active_chat=active_chat
    )


@messages_bp.route('/mensagens/enviar', methods=['POST'])
@login_required
def send_message():
    sender = g.current_user
    receiver_id = request.form.get('receiver_id', type=int)
    content = request.form.get('content', '').strip()

    if not receiver_id or not content:
        flash('Mensagem inválida.', 'danger')
        return redirect(url_for('messages.inbox'))

    receiver = User.query.get_or_404(receiver_id)

    msg = Message(
        sender_id=sender.id,
        receiver_id=receiver.id,
        content=content
    )
    db.session.add(msg)

    # Notificação para o destinatário
    notif = Notification(
        user_id=receiver.id,
        title='Nova Mensagem',
        message=f"{sender.display_name} enviou uma nova mensagem.",
        link=url_for('messages.inbox', user_id=sender.id)
    )
    db.session.add(notif)
    db.session.commit()

    if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'message': {
                'id': msg.id,
                'content': msg.content,
                'time': msg.created_at.strftime('%H:%M'),
                'is_sender': True
            }
        })

    return redirect(url_for('messages.inbox', user_id=receiver_id))


@messages_bp.route('/mensagens/api/conversa/<int:target_id>')
@login_required
def get_chat_messages(target_id):
    user = g.current_user
    msgs = Message.query.filter(
        ((Message.sender_id == user.id) & (Message.receiver_id == target_id)) |
        ((Message.sender_id == target_id) & (Message.receiver_id == user.id))
    ).order_by(Message.created_at.asc()).all()

    # Marcar recebidas como lidas
    for m in msgs:
        if m.receiver_id == user.id and not m.is_read:
            m.is_read = True
    db.session.commit()

    data = [{
        'id': m.id,
        'sender_id': m.sender_id,
        'content': m.content,
        'time': m.created_at.strftime('%H:%M'),
        'is_sender': (m.sender_id == user.id)
    } for m in msgs]

    return jsonify({'messages': data})
