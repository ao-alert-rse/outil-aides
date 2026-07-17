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
  secteur_naf text[],
  secteur_naf_exclu text[],
  opco text[],
  idcc text[],
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

-- Migration ponctuelle (2026-07-03) : conversion des colonnes tableau de
-- jsonb vers text[] (plus lisible/éditable dans le Table Editor Supabase,
-- aucun changement côté application — le SDK renvoie un tableau JS dans
-- les deux cas). À exécuter une seule fois sur une base créée avant cette
-- date. Passe par une colonne temporaire car Postgres n'autorise pas de
-- sous-requête dans la clause USING d'un ALTER COLUMN TYPE :
--
-- alter table aides add column opco_new text[];
-- update aides set opco_new = array(select jsonb_array_elements_text(opco)) where opco is not null;
-- alter table aides drop column opco;
-- alter table aides rename column opco_new to opco;
--
-- alter table aides add column idcc_new text[];
-- update aides set idcc_new = array(select jsonb_array_elements_text(idcc)) where idcc is not null;
-- alter table aides drop column idcc;
-- alter table aides rename column idcc_new to idcc;
--
-- alter table aides add column secteur_naf_new text[];
-- update aides set secteur_naf_new = array(select jsonb_array_elements_text(secteur_naf)) where secteur_naf is not null;
-- alter table aides drop column secteur_naf;
-- alter table aides rename column secteur_naf_new to secteur_naf;
--
-- alter table aides add column secteur_naf_exclu_new text[];
-- update aides set secteur_naf_exclu_new = array(select jsonb_array_elements_text(secteur_naf_exclu)) where secteur_naf_exclu is not null;
-- alter table aides drop column secteur_naf_exclu;
-- alter table aides rename column secteur_naf_exclu_new to secteur_naf_exclu;
