do $$
    begin
        INSERT INTO public.external_menu_sections VALUES (1, 'Кузовные запчасти');
        INSERT INTO public.external_menu_sections VALUES (2, 'Техничка');
        INSERT INTO public.external_menu_sections VALUES (3, 'Детали салона');
        INSERT INTO public.external_menu_sections VALUES (4, 'Электроника/Электрика');
        INSERT INTO public.external_menu_sections VALUES (5, 'Колеса');

        INSERT INTO public.internal_menu_sections VALUES (1, 'Бампер передний', 1);
        INSERT INTO public.internal_menu_sections VALUES (2, 'Бампер задний', 1);
        INSERT INTO public.internal_menu_sections VALUES (3, 'Капот', 1);
        INSERT INTO public.internal_menu_sections VALUES (4, 'Багажник', 1);
        INSERT INTO public.internal_menu_sections VALUES (5, 'Двери', 1);
        INSERT INTO public.internal_menu_sections VALUES (6, 'Разное', 1);

        INSERT INTO public.internal_menu_sections VALUES (7, 'Двигатель', 2);
        INSERT INTO public.internal_menu_sections VALUES (8, 'Навесное', 2);
        INSERT INTO public.internal_menu_sections VALUES (9, 'Охлаждение', 2);
        INSERT INTO public.internal_menu_sections VALUES (10, 'Кондиционер', 2);
        INSERT INTO public.internal_menu_sections VALUES (11, 'КПП', 2);
        INSERT INTO public.internal_menu_sections VALUES (12, 'Подвеска', 2);
        INSERT INTO public.internal_menu_sections VALUES (13, 'Тормоза', 2);
        INSERT INTO public.internal_menu_sections VALUES (14, 'Разное', 2);

        INSERT INTO public.internal_menu_sections VALUES (15, 'Детали проводки', 4);
        INSERT INTO public.internal_menu_sections VALUES (16, 'Электроника', 4);
        INSERT INTO public.internal_menu_sections VALUES (17, 'Блоки управления', 4);
        INSERT INTO public.internal_menu_sections VALUES (18, 'Разное', 4);

        INSERT INTO public.internal_menu_sections VALUES (19, 'Диски', 5);
        INSERT INTO public.internal_menu_sections VALUES (20, 'Резина', 5);
        INSERT INTO public.internal_menu_sections VALUES (21, 'Разное', 5);
        INSERT INTO public.internal_menu_sections VALUES (22, 'Колёса', 5);
    end
$$