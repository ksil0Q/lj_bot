do $$
    begin
        INSERT INTO public.external_menu_sections VALUES (1, '�������� ��������');
        INSERT INTO public.external_menu_sections VALUES (2, '��������');
        INSERT INTO public.external_menu_sections VALUES (3, '������ ������');
        INSERT INTO public.external_menu_sections VALUES (4, '�����������/���������');
        INSERT INTO public.external_menu_sections VALUES (5, '������');

        INSERT INTO public.internal_menu_sections VALUES (1, '������ ��������', 1);
        INSERT INTO public.internal_menu_sections VALUES (2, '������ ������', 1);
        INSERT INTO public.internal_menu_sections VALUES (3, '�����', 1);
        INSERT INTO public.internal_menu_sections VALUES (4, '��������', 1);
        INSERT INTO public.internal_menu_sections VALUES (5, '�����', 1);
        INSERT INTO public.internal_menu_sections VALUES (6, '������', 1);

        INSERT INTO public.internal_menu_sections VALUES (7, '���������', 2);
        INSERT INTO public.internal_menu_sections VALUES (8, '��������', 2);
        INSERT INTO public.internal_menu_sections VALUES (9, '����������', 2);
        INSERT INTO public.internal_menu_sections VALUES (10, '�����������', 2);
        INSERT INTO public.internal_menu_sections VALUES (11, '���', 2);
        INSERT INTO public.internal_menu_sections VALUES (12, '��������', 2);
        INSERT INTO public.internal_menu_sections VALUES (13, '�������', 2);
        INSERT INTO public.internal_menu_sections VALUES (14, '������', 2);

        INSERT INTO public.internal_menu_sections VALUES (15, '������ ��������', 4);
        INSERT INTO public.internal_menu_sections VALUES (16, '�����������', 4);
        INSERT INTO public.internal_menu_sections VALUES (17, '����� ����������', 4);
        INSERT INTO public.internal_menu_sections VALUES (18, '������', 4);

        INSERT INTO public.internal_menu_sections VALUES (19, '�����', 5);
        INSERT INTO public.internal_menu_sections VALUES (20, '������', 5);
        INSERT INTO public.internal_menu_sections VALUES (21, '������', 5);
        INSERT INTO public.internal_menu_sections VALUES (22, '�����', 5);
    end
$$