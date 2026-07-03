-- ══════════════════════════════════════════════
-- Schéma "aides" — structure de la table (sans données)
-- ══════════════════════════════════════════════
-- Note : ce fichier ne contient volontairement pas les données (114 aides).
-- La base compilée est une donnée propriétaire, protégée par la policy RLS
-- ci-dessous (lecture réservée aux utilisateurs authentifiés). Elle vit
-- uniquement dans Supabase, pas dans ce dépôt public.

create table if not exists aides (
  id text primary key,
  type text,
  nom text not null,
  description text,
  taux text,
  plafond text,
  origine text,
  effectif_min integer,
  effectif_max integer,
  region text,
  secteur_naf jsonb,
  secteur_naf_exclu jsonb,
  opco jsonb,
  idcc jsonb,
  lien text,
  derniere_verif date,
  montant_min numeric,
  montant_max numeric,
  duree text,
  date_fin date,
  plafond_variable boolean,
  nature text
);

alter table aides enable row level security;

create policy "aides_select_authenticated"
  on aides for select
  to authenticated
  using (true);

-- Migration ponctuelle (2026-07-03) : la fonctionnalité "plafond de minimis"
-- a été retirée de l'outil. Si la colonne minimis existe déjà sur une base
-- créée avant cette date, la supprimer avec :
-- alter table aides drop column if exists minimis;
