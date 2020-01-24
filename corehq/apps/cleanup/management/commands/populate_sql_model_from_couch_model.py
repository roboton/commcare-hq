import logging

from django.core.management.base import BaseCommand
from django.db import transaction

from dimagi.utils.couch.database import iter_docs

from corehq.dbaccessors.couchapps.all_docs import get_all_docs_with_doc_types, get_doc_count_by_type
from corehq.util.couchdb_management import couch_config

logger = logging.getLogger(__name__)


class PopulateSQLCommand(BaseCommand):
    """
        Base class for migrating couch docs to sql models.
    """
    AUTO_MIGRATE_ITEMS_LIMIT = 1000

    @classmethod
    def couch_db_slug(cls):
        # Override this if couch model was not stored in the main commcarehq database
        return None

    @classmethod
    def couch_doc_type(cls):
        raise NotImplementedError()

    @classmethod
    def couch_key(cls):
        """
        Set of doc keys to uniquely identify a couch document.
        For most documents this is set(["id"]), but sometimes it's useful to use a more
        human-readable key, typically for documents that have at most one doc per domain.
        """
        raise NotImplementedError()

    @classmethod
    def sql_class(self):
        raise NotImplementedError()

    def update_or_create_sql_object(self, doc):
        raise NotImplementedError()

    @classmethod
    def auto_migrate_failed_message(self):
        return """
            A migration must be performed before this environment can be upgraded to the latest version of CommCareHQ.
            This migration is run using the management command {}.
        """.format(__name__.split('.')[-1])

    @property
    def couch_db(self):
        return couch_config.get_db(self.couch_db_slug())

    def doc_key(self, doc):
        return {key: doc[key] for key in doc if key in self.couch_key()}

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            default=False,
            help='Do not actually modify the database, just verbosely log what will happen',
        )

    def handle(self, dry_run=False, **options):
        log_prefix = "[DRY RUN] " if dry_run else ""

        logger.info("{}Found {} {} docs and {} {} models".format(
            log_prefix,
            get_doc_count_by_type(self.couch_db, self.couch_doc_type()),
            self.couch_doc_type(),
            self.sql_class().objects.count(),
            self.sql_class().__name__,
        ))
        for doc in get_all_docs_with_doc_types(self.couch_db, [self.couch_doc_type()]):
            logger.info("{}Looking at doc with key {}".format(log_prefix, self.doc_key(doc)))
            with transaction.atomic():
                model, created = self.update_or_create_sql_object(doc)
                if not dry_run:
                    logger.info("{}{} model for doc with key {}".format(log_prefix,
                                                                        "Created" if created else "Updated",
                                                                        self.doc_key(doc)))
                    model.save()
                elif created:
                    model.delete()
