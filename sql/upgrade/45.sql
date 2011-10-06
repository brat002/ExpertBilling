                                             INSERT INTO helpdesk_emailtemplate (id, template_name, subject, heading, plain_text, html) VALUES (3, 'closed_cc', '(Closed)', 'Ticket Closed', 'Здравствуйте,

Сообщаем вам, что заявка {{ ticket.ticket }} была закрыта. {% if ticket.assigned_to %} Исполнитель заявки assigned to {{ ticket.assigned_to }}{% endif %}.

Номер заявки: {{ ticket.ticket }}
Тип завяки: {{ queue.title }}
Заголовок: {{ ticket.title }}
Открыта: {{ ticket.created|date:"l N jS Y, \\a\\t P" }}
Владелец: {{ ticket.owner}}
Приоритет: {{ ticket.get_priority_display }}
Статус: {{ ticket.get_status }}
Исполнитель: {{ ticket.get_assigned_to }}
URL заявки: {{ ticket.staff_url }}

Описание заявки:

{{ ticket.description }}
Решение:
{{ resolution }}', '<p style="font-family: sans-serif; font-size: 1em;">Здравствуйте,</p>

<p style="font-family: sans-serif; font-size: 1em;">Сообщаем вам, что  заявка {{ ticket.ticket }} была закрыта. {% if ticket.assigned_to %} Исполнитель заявки assigned to {{ ticket.assigned_to }}{% endif %}.</p>

<p style="font-family: sans-serif; font-size: 1em;">
<b>Номер заявки</b>: {{ ticket.ticket }}<br>
<b>Тип завяки</b>: {{ queue.title }}<br>
<b>Заголовок</b>: {{ ticket.title }}<br>
<b>Открыта</b>: {{ ticket.created|date:"l N jS Y, \\a\\t P" }}<br>
<b>Владелец</b>: {{ ticket.owner}}<br>
<b>Приоритет</b>: {{ ticket.get_priority_display }}<br>
<b>Статус</b>: {{ ticket.get_status }}<br>
<b>Исполнительto</b>: {{ ticket.get_assigned_to }}<br>
<b><a href=''{{ ticket.staff_url }}''>URL заявки</a></b> для просмотра заявки (требуется авторизация)</p>

<p style="font-family: sans-serif; font-size: 1em;">Описание заявки:</p>

<blockquote style="font-family: sans-serif; font-size: 1em;">{{ ticket.description }}</blockquote>

<p style="font-family: sans-serif; font-size: 1em;">Решение:</p>

<blockquote style="font-family: sans-serif; font-size: 1em;">{{ resolution }}</blockquote>

<p style="font-family: sans-serif; font-size: 1em;">Просмотреть заявку на сайте вы можете по ссылке <a href=''{{ ticket.staff_url }}''>{{ ticket.staff_url }}</a>.</p>');
INSERT INTO helpdesk_emailtemplate (id, template_name, subject, heading, plain_text, html) VALUES (2, 'assigned_to', '(Назначена на вас)', 'Заявка назначена на вас', 'Здравствуйте,

Сообщаем, что вам назначена заявка {{ ticket.ticket }}. {% if ticket.assigned_to %} Исполнитель заявки {{ ticket.assigned_to }}{% endif %}.

Номер заявки: {{ ticket.ticket }}
Тип завяки: {{ queue.title }}
Заголовок: {{ ticket.title }}
Открыта: {{ ticket.created|date:"l N jS Y, \\a\\t P" }}
Владелец: {{ ticket.owner}}
Приоритет: {{ ticket.get_priority_display }}
Статус: {{ ticket.get_status }}
Исполнитель: Вы
URL заявки: {{ ticket.staff_url }}

Описание заявки:

{{ ticket.description }}', '<p style="font-family: sans-serif; font-size: 1em;">Здравствуйте,</p>

<p style="font-family: sans-serif; font-size: 1em;">Сообщаем, что вам назначена заявка {{ ticket.ticket }}. {% if ticket.assigned_to %} Исполнитель заявки assigned to {{ ticket.assigned_to }}{% endif %}.</p>

<p style="font-family: sans-serif; font-size: 1em;">
<b>Номер заявки</b>: {{ ticket.ticket }}<br>
<b>Тип завяки</b>: {{ queue.title }}<br>
<b>Заголовок</b>: {{ ticket.title }}<br>
<b>Открыта</b>: {{ ticket.created|date:"l N jS Y, \\a\\t P" }}<br>
<b>Владелец</b>: {{ ticket.owner}}<br>
<b>Приоритет</b>: {{ ticket.get_priority_display }}<br>
<b>Статус</b>: {{ ticket.get_status }}<br>
<b>Исполнитель</b>: Вы<br>
<b><a href=''{{ ticket.staff_url }}''>URL заявки</a></b> для просмотра заявки (требуется авторизация)</p>

<p style="font-family: sans-serif; font-size: 1em;">Описание заявки:</p>

<blockquote style="font-family: sans-serif; font-size: 1em;">{{ ticket.description }}</blockquote>');
INSERT INTO helpdesk_emailtemplate (id, template_name, subject, heading, plain_text, html) VALUES (5, 'closed_owner', '(Закрыта)', 'Заявка закрыта', 'Здравствуйте,

Ваша заявка с темой "{{ ticket.title }}" была рассмотрена и закрыта.

Решение:

{{ ticket.resolution }}', '<p style="font-family: sans-serif; font-size: 1em;">Здравствуйте,</p>

<p style="font-family: sans-serif; font-size: 1em;">Ваша заявка с темой "{{ ticket.title }}" была рассмотрена и закрыта.</p>

<p style="font-family: sans-serif; font-size: 1em;">Решение:</p>

<blockquote style="font-family: sans-serif; font-size: 1em;">{{ ticket.resolution }}</blockquote>
');
INSERT INTO helpdesk_emailtemplate (id, template_name, subject, heading, plain_text, html) VALUES (6, 'escalated_cc', '(Escalated)', 'Ticket Escalated', 'Hello,

This is a courtesy e-mail to let you know that ticket {{ ticket.ticket }} ("{{ ticket.title }}") has been escalated automatically.

Ticket ID: {{ ticket.ticket }}
Queue: {{ queue.title }}
Title: {{ ticket.title }}
Opened: {{ ticket.created|date:"l N jS Y, \\a\\t P" }}
Submitter: {{ ticket.submitter_email|default:"Unknown" }}
Priority: {{ ticket.get_priority_display }}
Status: {{ ticket.get_status }}
Assigned to: {{ ticket.get_assigned_to }}
View Online: {{ ticket.staff_url }} (login required)

The original ticket description was:

{{ ticket.description }}', '<p style="font-family: sans-serif; font-size: 1em;">Hello,</p>

<p style="font-family: sans-serif; font-size: 1em;">This is a courtesy e-mail to let you know that ticket <i>{{ ticket.ticket }}</i> (''{{ ticket.title }}'') has been escalated automatically.</p>

<p style="font-family: sans-serif; font-size: 1em;">
<b>Ticket ID</b>: {{ ticket.ticket }}<br>
<b>Queue</b>: {{ queue.title }}<br>
<b>Title</b>: {{ ticket.title }}<br>
<b>Opened</b>: {{ ticket.created|date:"l N jS Y, \\a\\t P" }}<br>
<b>Submitter</b>: {{ ticket.submitter_email|default:"Unknown" }}<br>
<b>Priority</b>: {{ ticket.get_priority_display }}<br>
<b>Status</b>: {{ ticket.get_status }}<br>
<b>Assigned to</b>: {{ ticket.get_assigned_to }}<br>
<b><a href=''{{ ticket.staff_url }}''>View Online</a></b> to update this ticket (login required)</p>

<p style="font-family: sans-serif; font-size: 1em;">Just for reference, the original ticket description was:</p>

<blockquote style="font-family: sans-serif; font-size: 1em;">{{ ticket.description }}</blockquote>');
INSERT INTO helpdesk_emailtemplate (id, template_name, subject, heading, plain_text, html) VALUES (8, 'escalated_owner', '(Escalated)', 'Ticket Assigned to You Has Been Escalated', 'Hello,

A ticket currently assigned to you has been automatically escalated as it has been open for longer than expected.

Ticket ID: {{ ticket.ticket }}
Queue: {{ queue.title }}
Title: {{ ticket.title }}
Opened: {{ ticket.created|date:"l N jS Y, \\a\\t P" }}
Submitter: {{ ticket.submitter_email|default:"Unknown" }}
Priority: {{ ticket.get_priority_display }}
Status: {{ ticket.get_status }}
Assigned to: {{ ticket.get_assigned_to }}
View Online: {{ ticket.staff_url }} (login required)

The original ticket description was:

{{ ticket.description }}

Please review this ticket and attempt to provide a resolution as soon as possible.', '<p style="font-family: sans-serif; font-size: 1em;">Hello,</p>

<p style="font-family: sans-serif; font-size: 1em;">A ticket currently assigned to you has been automatically escalated as it has been open for longer than expected.</p>

<p style="font-family: sans-serif; font-size: 1em;">
<b>Ticket ID</b>: {{ ticket.ticket }}<br>
<b>Queue</b>: {{ queue.title }}<br>
<b>Title</b>: {{ ticket.title }}<br>
<b>Opened</b>: {{ ticket.created|date:"l N jS Y, \\a\\t P" }}<br>
<b>Submitter</b>: {{ ticket.submitter_email|default:"Unknown" }}<br>
<b>Priority</b>: {{ ticket.get_priority_display }}<br>
<b>Status</b>: {{ ticket.get_status }}<br>
<b>Assigned to</b>: {{ ticket.get_assigned_to }}<br>
<b><a href=''{{ ticket.staff_url }}''>View Online</a></b> to update this ticket (login required)</p>

<p style="font-family: sans-serif; font-size: 1em;">Just for reference, the original ticket description was:</p>

<blockquote style="font-family: sans-serif; font-size: 1em;">{{ ticket.description }}</blockquote>');
INSERT INTO helpdesk_emailtemplate (id, template_name, subject, heading, plain_text, html) VALUES (7, 'escalated_submitter', '(Escalated)', 'Your Ticket Has Been Escalated', 'Hello,

You recently logged a ticket with a subject of "{{ ticket.title }}" with us. This e-mail is to advise you of an automated escalation of that ticket as it has been open for longer than expected.

We will review your ticket shortly and attempt to provide a resolution as soon as possible.

If you wish to view this ticket online, you can visit {{ ticket.ticket_url }}.', '<p style="font-family: sans-serif; font-size: 11pt;">Hello,</p>

<p style="font-family: sans-serif; font-size: 11pt;">You recently logged a ticket with a subject of <i>{{ ticket.title }}</i> with us. This e-mail is to advise you of an automated escalation of that ticket as it has been open for longer than expected.</p>

<p style="font-family: sans-serif; font-size: 11pt;">We will review your ticket shortly and attempt to provide a resolution as soon as possible.</p>

<p style="font-family: sans-serif; font-size: 11pt;">If you wish to view this ticket online, you can visit <a href="{{ ticket.ticket_url }}">{{ ticket.ticket_url }}</a>.</p>');
INSERT INTO helpdesk_emailtemplate (id, template_name, subject, heading, plain_text, html) VALUES (10, 'newticket_owner', '(Новая)', 'Ваша заявка была добавлена', 'Здравствуйте,

Сообщаем, что ваша заявка "{{ ticket.title }}" была добавлена в базу HelpDesk. 
Просмотреть заявку вы можете по этой ссылке {{ ticket.ticket_url }}.

', '<p style="font-family: sans-serif; font-size: 1em;">Здравствуйте,</p>

<p style="font-family: sans-serif; font-size: 1em;">Сообщаем, что ваша заявка "{{ ticket.title }}" была добавлена в базу HelpDesk. </p>

<p style="font-family: sans-serif; font-size: 1em;">Просмотреть заявку вы можете по этой ссылке {{ ticket.ticket_url }}.</p>
');
INSERT INTO helpdesk_emailtemplate (id, template_name, subject, heading, plain_text, html) VALUES (13, 'resolved_owner', '(Выполнена)', 'Ваша заявка была выполнена', 'Здравствуйте,

Ваша заявка "{{ ticket.title }}" была выполнена.

Ответ по заявке {{ ticket.ticket }}:

{{ resolution }}

Адрес заявки {{ ticket.ticket_url }}.', '<p style="font-family: sans-serif; font-size: 1em;">Здравствуйте,</p>

<p style="font-family: sans-serif; font-size: 1em;">Ваша заявка "{{ ticket.title }}" была выполнена.</p>

<p style="font-family: sans-serif; font-size: 1em;">Ответ по заявке {{ ticket.ticket }}:</b>:</p>

<blockquote style="font-family: sans-serif; font-size: 1em;">{{ resolution }}</blockquote>

<p style="font-family: sans-serif; font-size: 1em;">Адрес заявки <a href="{{ ticket.ticket_url }}">{{ ticket.ticket_url }}</a>.</p>');
INSERT INTO helpdesk_emailtemplate (id, template_name, subject, heading, plain_text, html) VALUES (14, 'updated_cc', '(Изменение)', 'Изменения в заявке', 'Здравствуйте,

В вашей заявке ест новые изменения {{ ticket.ticket }} ("{{ ticket.title }}").

Номер заявки: {{ ticket.ticket }}
Тип завяки: {{ queue.title }}
Заголовок: {{ ticket.title }}
Открыта: {{ ticket.created|date:"l N jS Y, \\a\\t P" }}
Владелец: {{ ticket.owner}}
Приоритет: {{ ticket.get_priority_display }}
Статус: {{ ticket.get_status }}
Исполнитель: {{ ticket.get_assigned_to }}
URL заявки: {{ ticket.staff_url }}

Описание:

{{ ticket.description }}

Следующие изменения:

{{ comment }}

This information has {% if private %}not {% endif %} been e-mailed to the submitter.
', '<p style="font-family: sans-serif; font-size: 1em;">Hello,</p>

<p style="font-family: sans-serif; font-size: 1em;">This is a courtesy e-mail to let you know that ticket {{ ticket.ticket }} ("{{ ticket.title }}") for {{ ticket.submitter_email }} has been updated.</p>

<p style="font-family: sans-serif; font-size: 1em;">
<b>Ticket ID</b>: {{ ticket.ticket }}<br>
<b>Queue</b>: {{ queue.title }}<br>
<b>Title</b>: {{ ticket.title }}<br>
<b>Opened</b>: {{ ticket.created|date:"l N jS Y, \\a\\t P" }}<br>
<b>Submitter</b>: {{ ticket.submitter_email|default:"Unknown" }}<br>
<b>Priority</b>: {{ ticket.get_priority_display }}<br>
<b>Status</b>: {{ ticket.get_status }}<br>
<b>Assigned to</b>: {{ ticket.get_assigned_to }}<br>
<b><a href=''{{ ticket.staff_url }}''>View Online</a></b> to update this ticket (login required)</p>

<p style="font-family: sans-serif; font-size: 1em;">Just for reference, the original ticket description was:</p>

<blockquote style="font-family: sans-serif; font-size: 1em;">{{ ticket.description }}</blockquote>

<p style="font-family: sans-serif; font-size: 1em;">The following comment was added:</p>

<blockquote style="font-family: sans-serif; font-size: 1em;">{{ comment }}</blockquote>

<p style="font-family: Tahoma, Arial, sans-serif; font-size: 11pt;">This information has {% if private %}not {% endif %} been e-mailed to the submitter.</p>');
INSERT INTO helpdesk_emailtemplate (id, template_name, subject, heading, plain_text, html) VALUES (1, 'assigned_cc', '(В работе)', 'Заявка пинята в работу', 'Здравствуйте,

Сообщаем вам, что мы начали работу над вашей заявкой {{ ticket.ticket }}. {% if ticket.assigned_to %} Исполнитель заявки assigned to {{ ticket.assigned_to }}{% endif %}.

Номер заявки: {{ ticket.ticket }}
Тип завяки: {{ queue.title }}
Заголовок: {{ ticket.title }}
Открыта: {{ ticket.created|date:"l N jS Y, \\a\\t P" }}
Владелец: {{ ticket.owner}}
Приоритет: {{ ticket.get_priority_display }}
Статус: {{ ticket.get_status }}
Исполнитель: {{ ticket.get_assigned_to }}
URL заявки: {{ ticket.staff_url }}

Описание заявки:

{{ ticket.description }}', '<p style="font-family: sans-serif; font-size: 1em;">Здравствуйте,</p>

<p style="font-family: sans-serif; font-size: 1em;">Сообщаем вам, что мы начали работу над вашей заявкой {{ ticket.ticket }}. {% if ticket.assigned_to %} Исполнитель заявки assigned to {{ ticket.assigned_to }}{% endif %}.</p>

<p style="font-family: sans-serif; font-size: 1em;">
<b>Номер заявки</b>: {{ ticket.ticket }}<br>
<b>Тип завяки</b>: {{ queue.title }}<br>
<b>Заголовок</b>: {{ ticket.title }}<br>
<b>Открыта</b>: {{ ticket.created|date:"l N jS Y, \\a\\t P" }}<br>
<b>Владелец</b>: {{ ticket.owner}}<br>
<b>Приоритет</b>: {{ ticket.get_priority_display }}<br>
<b>Статус</b>: {{ ticket.get_status }}<br>
<b>Исполнительto</b>: {{ ticket.get_assigned_to }}<br>
<b><a href=''{{ ticket.staff_url }}''>URL заявки</a></b> для просмотра заявки (требуется авторизация)</p>

<p style="font-family: sans-serif; font-size: 1em;">Описание заявки:</p>

<blockquote style="font-family: sans-serif; font-size: 1em;">{{ ticket.description }}</blockquote>');
INSERT INTO helpdesk_emailtemplate (id, template_name, subject, heading, plain_text, html) VALUES (16, 'updated_owner', '(Изменение)', 'Ваша заявка была обновлена', 'Здравствуйте,

Ваша заявка "{{ ticket.title }}" была обновлена.

Был добавлен следующий комментарий:

{{ comment }}

Просмотреть заявку вы можете по этой ссылке {{ ticket.ticket_url }}.', 'Здравствуйте,

Ваша заявка "{{ ticket.title }}" была обновлена.

Был добавлен следующий комментарий:

{{ comment }}

Просмотреть заявку вы можете по этой ссылке {{ ticket.ticket_url }}.');
INSERT INTO helpdesk_emailtemplate (id, template_name, subject, heading, plain_text, html) VALUES (4, 'closed_assigned_to', '(Закрыта)', 'Заявка закрыта', 'Здравствуйте,

Сообщаем вам, что заявка {{ ticket.ticket }} была закрыта. {% if ticket.assigned_to %} Исполнитель заявки assigned to {{ ticket.assigned_to }}{% endif %}.

Номер заявки: {{ ticket.ticket }}
Тип завяки: {{ queue.title }}
Заголовок: {{ ticket.title }}
Открыта: {{ ticket.created|date:"l N jS Y, \\a\\t P" }}
Владелец: {{ ticket.owner}}
Приоритет: {{ ticket.get_priority_display }}
Статус: {{ ticket.get_status }}
Исполнитель: {{ ticket.get_assigned_to }}
URL заявки: {{ ticket.staff_url }}

Описание заявки:

{{ ticket.description }}', '<p style="font-family: sans-serif; font-size: 1em;">Здравствуйте,</p>

<p style="font-family: sans-serif; font-size: 1em;">Сообщаем вам, что ваша заявка {{ ticket.ticket }} была закрыта. {% if ticket.assigned_to %} Исполнитель заявки assigned to {{ ticket.assigned_to }}{% endif %}.</p>

<p style="font-family: sans-serif; font-size: 1em;">
<b>Номер заявки</b>: {{ ticket.ticket }}<br>
<b>Тип завяки</b>: {{ queue.title }}<br>
<b>Заголовок</b>: {{ ticket.title }}<br>
<b>Открыта</b>: {{ ticket.created|date:"l N jS Y, \\a\\t P" }}<br>
<b>Владелец</b>: {{ ticket.owner}}<br>
<b>Приоритет</b>: {{ ticket.get_priority_display }}<br>
<b>Статус</b>: {{ ticket.get_status }}<br>
<b>Исполнительto</b>: {{ ticket.get_assigned_to }}<br>
<b><a href=''{{ ticket.staff_url }}''>URL заявки</a></b> для просмотра заявки (требуется авторизация)</p>

<p style="font-family: sans-serif; font-size: 1em;">Описание заявки:</p>

<blockquote style="font-family: sans-serif; font-size: 1em;">{{ ticket.description }}</blockquote>');
INSERT INTO helpdesk_emailtemplate (id, template_name, subject, heading, plain_text, html) VALUES (9, 'newticket_cc', '(Новая)', 'Создана новая заявка', 'Здравствуйте,

Сообщаем, что в HelpDesk появилась новая заявка

Номер заявки: {{ ticket.ticket }}
Тип завяки: {{ queue.title }}
Заголовок: {{ ticket.title }}
Открыта: {{ ticket.created|date:"l N jS Y, \\a\\t P" }}
Владелец: {{ ticket.owner}}
Приоритет: {{ ticket.get_priority_display }}
Статус: {{ ticket.get_status }}
Исполнитель: {{ ticket.get_assigned_to }}
URL заявки: {{ ticket.staff_url }}

Описание:
{{ ticket.description }}
', '<p style="font-family: sans-serif; font-size: 1em;">Здравствуйте,</p>

<p style="font-family: sans-serif; font-size: 1em;">Сообщаем вам, что в HelpDesk появилась новая заявка {{ ticket.ticket }}. </p>

<p style="font-family: sans-serif; font-size: 1em;">
<b>Номер заявки</b>: {{ ticket.ticket }}<br>
<b>Тип завяки</b>: {{ queue.title }}<br>
<b>Заголовок</b>: {{ ticket.title }}<br>
<b>Открыта</b>: {{ ticket.created|date:"l N jS Y, \\a\\t P" }}<br>
<b>Владелец</b>: {{ ticket.owner}}<br>
<b>Приоритет</b>: {{ ticket.get_priority_display }}<br>
<b>Статус</b>: {{ ticket.get_status }}<br>
<b>Исполнительto</b>: {{ ticket.get_assigned_to }}<br>
<b><a href=''{{ ticket.staff_url }}''>URL заявки</a></b> для просмотра заявки (требуется авторизация)</p>

<p style="font-family: sans-serif; font-size: 1em;">Описание заявки:</p>

<blockquote style="font-family: sans-serif; font-size: 1em;">{{ ticket.description }}</blockquote>');
INSERT INTO helpdesk_emailtemplate (id, template_name, subject, heading, plain_text, html) VALUES (11, 'resolved_cc', '(Выполнена)', 'Заявка выполнена', 'Здравствуйте,

Следующая заявка была выполнена:

Номер заявки: {{ ticket.ticket }}
Тип завяки: {{ queue.title }}
Заголовок: {{ ticket.title }}
Открыта: {{ ticket.created|date:"l N jS Y, \\a\\t P" }}
Владелец: {{ ticket.owner}}
Приоритет: {{ ticket.get_priority_display }}
Статус: {{ ticket.get_status }}
Исполнитель: {{ ticket.get_assigned_to }}
URL заявки: {{ ticket.staff_url }}

Решение:

{{ ticket.resolution }}

Решение было отправлено владельцу.', '<p style="font-family: sans-serif; font-size: 1em;">Здравствуйте,</p>

<p style="font-family: sans-serif; font-size: 1em;">Следующая заявка была выполнена.</p>

<p style="font-family: sans-serif; font-size: 1em;">
<b>Номер заявки</b>: {{ ticket.ticket }}<br>
<b>Тип завяки</b>: {{ queue.title }}<br>
<b>Заголовок</b>: {{ ticket.title }}<br>
<b>Открыта</b>: {{ ticket.created|date:"l N jS Y, \\a\\t P" }}<br>
<b>Владелец</b>: {{ ticket.owner}}<br>
<b>Приоритет</b>: {{ ticket.get_priority_display }}<br>
<b>Статус</b>: {{ ticket.get_status }}<br>
<b>Исполнительto</b>: {{ ticket.get_assigned_to }}<br>
<b><a href=''{{ ticket.staff_url }}''>URL заявки</a></b> для просмотра заявки (требуется авторизация)</p>

<p style="font-family: sans-serif; font-size: 1em;">Описание заявки:</p>

<blockquote style="font-family: sans-serif; font-size: 1em;">{{ ticket.description }}</blockquote>

<p style="font-family: sans-serif; font-size: 1em;">Решение:</p>

<blockquote style="font-family: sans-serif; font-size: 1em;">{{ ticket.resolution }}</blockquote>

<p style="font-family: sans-serif; font-size: 1em;">Решение было отправлено владельцу.</p>');
INSERT INTO helpdesk_emailtemplate (id, template_name, subject, heading, plain_text, html) VALUES (12, 'resolved_assigned_to', '(Выполнена)', 'Заявка выполнена', 'HЗдравствуйте,

Назначенная на вас заявка была выполнена.
Номер заявки: {{ ticket.ticket }}
Тип завяки: {{ queue.title }}
Заголовок: {{ ticket.title }}
Открыта: {{ ticket.created|date:"l N jS Y, \\a\\t P" }}
Владелец: {{ ticket.owner}}
Приоритет: {{ ticket.get_priority_display }}
Статус: {{ ticket.get_status }}
Исполнитель: {{ ticket.get_assigned_to }}
URL заявки: {{ ticket.staff_url }}

Описание заявки:

{{ ticket.description }}

Решение:

{{ ticket.resolution }}
', '<p style="font-family: sans-serif; font-size: 1em;">Здравствуйте,</p>

<p style="font-family: sans-serif; font-size: 1em;">Назначенная на вас заявка была выполнена.</p>


<p style="font-family: sans-serif; font-size: 1em;">
<b>Номер заявки</b>: {{ ticket.ticket }}<br>
<b>Тип завяки</b>: {{ queue.title }}<br>
<b>Заголовок</b>: {{ ticket.title }}<br>
<b>Открыта</b>: {{ ticket.created|date:"l N jS Y, \\a\\t P" }}<br>
<b>Владелец</b>: {{ ticket.owner}}<br>
<b>Приоритет</b>: {{ ticket.get_priority_display }}<br>
<b>Статус</b>: {{ ticket.get_status }}<br>
<b>Исполнительto</b>: {{ ticket.get_assigned_to }}<br>
<b><a href=''{{ ticket.staff_url }}''>URL заявки</a></b> для просмотра заявки (требуется авторизация)</p>

<p style="font-family: sans-serif; font-size: 1em;">Описание заявки:</p>

<blockquote style="font-family: sans-serif; font-size: 1em;">{{ ticket.description }}</blockquote>

<p style="font-family: sans-serif; font-size: 1em;">Решение:</p>

<blockquote style="font-family: sans-serif; font-size: 1em;">{{ ticket.resolution }}</blockquote>
');
INSERT INTO helpdesk_emailtemplate (id, template_name, subject, heading, plain_text, html) VALUES (15, 'updated_assigned_to', '(Изменения)', 'Изменения в заявке', 'Здравствуйте,

В вашей заявке были изменения {{ ticket.ticket }} ("{{ ticket.title }}").

Номер заявки: {{ ticket.ticket }}
Тип завяки: {{ queue.title }}
Заголовок: {{ ticket.title }}
Открыта: {{ ticket.created|date:"l N jS Y, \\a\\t P" }}
Владелец: {{ ticket.owner}}
Приоритет: {{ ticket.get_priority_display }}
Статус: {{ ticket.get_status }}
Исполнитель: {{ ticket.get_assigned_to }}
URL заявки: {{ ticket.staff_url }}

Описание:

{{ ticket.description }}

Следующий комментарий был добавлен:

{{ comment }}

This information has {% if private %}not {% endif %} been e-mailed to the submitter.', '<p style="font-family: sans-serif; font-size: 1em;">Здравствуйте,</p>

<p style="font-family: sans-serif; font-size: 1em;">В вашей заявке были изменения {{ ticket.ticket }} ("{{ ticket.title }}").</p>


<p style="font-family: sans-serif; font-size: 1em;">
<b>Номер заявки</b>: {{ ticket.ticket }}<br>
<b>Тип завяки</b>: {{ queue.title }}<br>
<b>Заголовок</b>: {{ ticket.title }}<br>
<b>Открыта</b>: {{ ticket.created|date:"l N jS Y, \\a\\t P" }}<br>
<b>Владелец</b>: {{ ticket.owner}}<br>
<b>Приоритет</b>: {{ ticket.get_priority_display }}<br>
<b>Статус</b>: {{ ticket.get_status }}<br>
<b>Исполнительto</b>: {{ ticket.get_assigned_to }}<br>
<b><a href=''{{ ticket.staff_url }}''>URL заявки</a></b> для просмотра заявки (требуется авторизация)</p>

<p style="font-family: sans-serif; font-size: 1em;">Описание:</p>

<blockquote style="font-family: sans-serif; font-size: 1em;">{{ ticket.description }}</blockquote>

<p style="font-family: sans-serif; font-size: 1em;">Следующий комментарий был добавлен:</p>

<blockquote style="font-family: sans-serif; font-size: 1em;">{{ comment }}</blockquote>

<p style="font-family: Tahoma, Arial, sans-serif; font-size: 11pt;">This information has {% if private %}not {% endif %} been e-mailed to the submitter.</p>');
