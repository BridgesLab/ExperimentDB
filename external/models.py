"""This package contains the model information for the external app.

It defines the structure and behavior of the following models:
* Contact
* Vendor
* Reference

"""
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.db import models

#Publication types are based on http://apidocs.mendeley.com/home/documenttypes
PUBLICATION_TYPES = (
	('Most Common', (
			('journal-article','Journal Article'),
			('book-section', 'Book Section'),
			)
	),
	('Less Common', (		
		('bill', 'Bill'),
		('book', 'Book'),
		('case', 'Case'),
		('computer-program', 'Computer Program'),
		('conference-proceedings', 'Conference Proceedings'),
		('encyclopedia-article', 'Encyclopedia Article'),
		('film', 'Film'),
		('generic', 'Generic'),
		('magazine-article','Magazine Article'),
		('newspaper-article','Newspaper Article'),
		('patent', 'Patent'),
		('report','Report'),
		('statute', 'Statute'),
		('television-broadcast', 'Television Broadcast'),
		('web-page', 'Web Page'),
		)
	),
)

class Contact(models.Model):
    """This model defines a contact.

    This is intended to be a person who is involved in the research program, and may be but it not necessarily a database user.
    The required fields are first_name and last_name.
    """
    first_name = models.CharField(max_length=25)
    middle_names = models.CharField(max_length=25, blank=True, null=True)
    last_name = models.CharField(max_length=25)
    user = models.ForeignKey(User, blank=True, null=True, help_text="Select from the list if the contact is also a database user")
    contactID = models.SlugField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    address = models.TextField(max_length=500, blank=True, null=True)
    comments = models.TextField(max_length=250, blank=True, null=True)
    public = models.BooleanField()
    class Meta:
        ordering = ['last_name',]
	
    def __unicode__(self):
        return u'%s %s' % (self.first_name, self.last_name)
   
    @models.permalink
    def get_absolute_url(self):
        return ('contact-detail', [str(self.id)])

    def save(self):
        """The save is over-ridden to slugify the contact field into a slugfield named contactID."""
        self.contactID = slugify( self.__unicode__() )
        super( Contact, self ).save()

class Reference(models.Model):
    '''This model covers publications of several types.
    
    The publication fields are based on Mendeley and PubMed fields.
    For the author, there is a ManyToMany link to a group of authors with the order and other details.  See `::class:AuthorDetails`.
    '''
    mendeley_url = models.URLField(blank=True, null=True)
    title = models.CharField(max_length=150)
    authors = models.ManyToManyField('AuthorDetails', blank=True, null=True)
    title_slug = models.SlugField(blank=True, null=True, max_length=150)
    mendeley_id = models.IntegerField(blank=True, null=True)
    doi = models.CharField(blank=True, null=True, max_length=50, help_text="Digital Object Identifier", verbose_name="DOI")
    pmid = models.IntegerField(blank=True, null=True, help_text='PubMed Idenfifier', verbose_name="PMID")
    pmcid = models.IntegerField(blank=True, null=True, help_text='PubMed Central Idenfifier', verbose_name="PMCID")    
    journal = models.CharField(max_length=100, blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    volume = models.CharField(max_length=15, blank=True, null=True)    
    issue = models.CharField(max_length=15, blank=True, null=True)
    pages = models.CharField(max_length=15, blank=True, null=True)
    abstract = models.TextField(blank=True, null=True)
    type = models.CharField(choices = PUBLICATION_TYPES, max_length=20, blank=True, null=True)
    laboratory_paper = models.BooleanField(help_text="Is this paper from our lab?")
    interesting_paper = models.BooleanField(help_text="Is this paper of interest but from another lab?")
    date_last_modified = models.DateField(auto_now=True)
    date_added = models.DateField(auto_now_add=True)    
    
    def doi_link(self):
        '''This turns the DOI into a link.'''
        return 'http://dx.doi.org/%s' % self.doi
        
    def full_pmcid(self):
        '''Converts the integer to a full PMCID'''
        return 'PMC%s' % self.pmcid    
    
    def __unicode__(self):
        '''The unicode representation for a Publication is its title'''
        return self.title
        
    @models.permalink
    def get_absolute_url(self):
        '''the permalink for a paper detail page is /papers/[title_slug]'''
        return ('paper-details', [str(self.title_slug)])   

    def save(self, *args, **kwargs):
        '''The title is slugified upon saving into title_slug.'''
        if not self.id:
            self.title_slug = slugify(self.title)
        super(Reference, self).save(*args, **kwargs)
        
class AuthorDetails(models.Model):
    '''This is a group of authors for a specific paper.
        
    Because each `::class:Reference` has a list of authors and the order matters, the authors are listed in this linked model.
    This model has a ManyToMany link with a paper as well as marks for order, and whether an author is a corresponding or equally contributing author.
    '''
    author = models.ForeignKey('Contact')
    order = models.IntegerField(help_text='The order in which the author appears (do not duplicate numbers)')
    corresponding_author = models.BooleanField()
    equal_contributors = models.BooleanField(help_text='Check both equally contributing authors')
        
    def __unicode__(self):
        '''The unicode representation is the author name.'''
        return '%s' %self.author
	
class Vendor(models.Model):
    """This model contains objects of the class vendor.

    It is intended to be used to indicate companies from which reagents are obtained.
    The only required field is company."""
    company = models.CharField(max_length = 100)
    company_slug = models.SlugField(max_length = 100, help_text="Will be set automatically upon saving")
    class Meta:
	ordering = ['company',]

    def __unicode__(self):
        return u'%s' % self.company

    @models.permalink
    def get_absolute_url(self):
        return ('vendor-detail', [str(self.id)])

    def save(self):
        """The save is over-ridden to slugify the contact field into a slugfield named contactID."""
        self.company_slug = slugify( self.__unicode__() )
        super( Vendor, self ).save()
