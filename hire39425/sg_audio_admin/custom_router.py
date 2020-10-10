# encoding:utf-8
class CustomerRouter(object):
    """
    A router to control all database operations on models in the
    customer application.
    """

    def db_for_read(self, model, **hints):
        """
        Attempts to read customer models go to customer.
        """
        if model._meta.app_label == 'default':
            return 'customer'
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write customer models go to customer.
        """
        if model._meta.app_label == 'default':
            return 'customer'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the customer app is involved.
        """
        if obj1._meta.app_label == 'default' or \
                obj2._meta.app_label == 'default':
            return True
        return None

    def allow_migrate(self, db, app_label, model=None, **hints):
        """
        Make sure the customer app only appears in the 'default'
        database.
        """
        if app_label == 'default':
            return db == 'default'
        return None
