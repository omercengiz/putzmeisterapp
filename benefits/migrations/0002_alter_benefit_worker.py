# benefits/migrations/0002_benefit_schema_update.py
from django.db import migrations

UP_SQL = """
BEGIN;

-- 1) Yeni kolonları ekle (yoksa)
ALTER TABLE benefits
    ADD COLUMN IF NOT EXISTS aile_yakacak    NUMERIC(12,2) NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS erzak           NUMERIC(12,2) NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS altin           NUMERIC(12,2) NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS bayram          NUMERIC(12,2) NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS dogum_evlenme   NUMERIC(12,2) NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS fon             NUMERIC(12,2) NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS harcirah        NUMERIC(12,2) NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS yol_parasi      NUMERIC(12,2) NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS prim            NUMERIC(12,2) NOT NULL DEFAULT 0;

-- 2) Veri taşıma (eski kolonlar varsa)
-- harcırah = yurtici + yurtdisi
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'benefits' AND column_name = 'yurtici_harcirah'
    ) AND EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'benefits' AND column_name = 'yurtdisi_harcirah'
    ) THEN
        UPDATE benefits
        SET harcirah = COALESCE(yurtici_harcirah,0) + COALESCE(yurtdisi_harcirah,0);
    END IF;
END$$;

-- doğum_evlenme = dogum_yardimi + evlenme_yardimi
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'benefits' AND column_name = 'dogum_yardimi'
    ) AND EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'benefits' AND column_name = 'evlenme_yardimi'
    ) THEN
        UPDATE benefits
        SET dogum_evlenme = COALESCE(dogum_yardimi,0) + COALESCE(evlenme_yardimi,0);
    END IF;
END$$;

-- yol_parasi = yol_yardimi
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'benefits' AND column_name = 'yol_yardimi'
    ) THEN
        UPDATE benefits
        SET yol_parasi = COALESCE(yol_yardimi,0);
    END IF;
END$$;

-- (Opsiyonel) erzak = yemek_ticket (eğer aynı anlamdaysa)
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'benefits' AND column_name = 'yemek_ticket'
    ) THEN
        UPDATE benefits
        SET erzak = COALESCE(yemek_ticket,0);
    END IF;
END$$;

-- 3) Eski kolonları düşür
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='benefits' AND column_name='yurtici_harcirah')
    THEN EXECUTE 'ALTER TABLE benefits DROP COLUMN yurtici_harcirah'; END IF;

    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='benefits' AND column_name='yurtdisi_harcirah')
    THEN EXECUTE 'ALTER TABLE benefits DROP COLUMN yurtdisi_harcirah'; END IF;

    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='benefits' AND column_name='yol_yardimi')
    THEN EXECUTE 'ALTER TABLE benefits DROP COLUMN yol_yardimi'; END IF;

    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='benefits' AND column_name='yemek_ticket')
    THEN EXECUTE 'ALTER TABLE benefits DROP COLUMN yemek_ticket'; END IF;

    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='benefits' AND column_name='dogum_yardimi')
    THEN EXECUTE 'ALTER TABLE benefits DROP COLUMN dogum_yardimi'; END IF;

    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='benefits' AND column_name='evlenme_yardimi')
    THEN EXECUTE 'ALTER TABLE benefits DROP COLUMN evlenme_yardimi'; END IF;
END$$;

COMMIT;
"""

DOWN_SQL = """
BEGIN;

-- rollback için eski kolonları geri ekle (boş default ile)
ALTER TABLE benefits
    ADD COLUMN IF NOT EXISTS yurtici_harcirah   NUMERIC(12,2) NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS yurtdisi_harcirah  NUMERIC(12,2) NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS yol_yardimi        NUMERIC(12,2) NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS yemek_ticket       NUMERIC(12,2) NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS dogum_yardimi      NUMERIC(12,2) NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS evlenme_yardimi    NUMERIC(12,2) NOT NULL DEFAULT 0;

-- veri geri dönüş mantığı basit tutuldu (istenirse genişletilebilir)
-- yeni kolonları drop et
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='benefits' AND column_name='aile_yakacak')
    THEN EXECUTE 'ALTER TABLE benefits DROP COLUMN aile_yakacak'; END IF;

    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='benefits' AND column_name='erzak')
    THEN EXECUTE 'ALTER TABLE benefits DROP COLUMN erzak'; END IF;

    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='benefits' AND column_name='altin')
    THEN EXECUTE 'ALTER TABLE benefits DROP COLUMN altin'; END IF;

    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='benefits' AND column_name='bayram')
    THEN EXECUTE 'ALTER TABLE benefits DROP COLUMN bayram'; END IF;

    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='benefits' AND column_name='dogum_evlenme')
    THEN EXECUTE 'ALTER TABLE benefits DROP COLUMN dogum_evlenme'; END IF;

    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='benefits' AND column_name='fon')
    THEN EXECUTE 'ALTER TABLE benefits DROP COLUMN fon'; END IF;

    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='benefits' AND column_name='harcirah')
    THEN EXECUTE 'ALTER TABLE benefits DROP COLUMN harcirah'; END IF;

    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='benefits' AND column_name='yol_parasi')
    THEN EXECUTE 'ALTER TABLE benefits DROP COLUMN yol_parasi'; END IF;

    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='benefits' AND column_name='prim')
    THEN EXECUTE 'ALTER TABLE benefits DROP COLUMN prim'; END IF;
END$$;

COMMIT;
"""

class Migration(migrations.Migration):

    dependencies = [
        ('benefits', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(sql=UP_SQL, reverse_sql=DOWN_SQL),
    ]
