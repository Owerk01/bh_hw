from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class Student(models.Model):
    name = models.CharField(max_length=20,
                            verbose_name='Имя',
                            null=False,
                            blank=False)
    
    surname = models.CharField(max_length=20,
                               verbose_name='Фамилия',
                               null=False,
                               blank=False)
    
    age = models.SmallIntegerField(validators=[MinValueValidator(18), 
                                               MaxValueValidator(99)],
                                        null=False,
                                        blank=False,
                                        verbose_name='Возраст')
    
    gender = models.CharField(choices=[('m', 'Мужской'), ('f', 'Женский')],
                                 null=True,
                                 blank=True, 
                                 verbose_name='Пол')
    
    active = models.BooleanField(verbose_name='Активный', 
                                 null=True, 
                                 blank=True)
    
    courses = models.ManyToManyField(to='Course',
                                    blank=True,
                                    verbose_name='Посещаемые курсы',
                                    related_name='Students')
    
    def __str__(self):
        return f'{self.surname} {self.name}'
    
    class Meta:
        verbose_name = 'Студент'
        verbose_name_plural = 'Студенты'
        indexes = [models.Index(fields=['surname'])]
        unique_together = [['name', 'surname']]
        ordering = ['surname']


class Course(models.Model):
    langs = [
        ('py', 'python'),
        ('js', 'JavaScript'),
        ('c', 'C++'),
        ('an', 'Android')
    ]

    name = models.CharField(choices=langs,
                            verbose_name='Курс',
                            null=False,
                            blank=False)
    
    course_num = models.SmallIntegerField(default=1,
                                          verbose_name='Номер курса',
                                          validators=[MinValueValidator(1),
                                                      MaxValueValidator(100)],)
    
    start_date = models.DateField(verbose_name='Дата начала',
                                  null=True)
    
    end_date = models.DateField(verbose_name='Дата окончания',
                                null=True)
    
    description = models.TextField(verbose_name='Описание', blank=True)

    def __str__(self):
        return f'{self.name} - {self.course_num}'
    
    class Meta:
        unique_together = [['name', 'course_num']]
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        ordering = ['name', 'course_num']


class Grade(models.Model):
    grade = models.PositiveSmallIntegerField(validators=[MinValueValidator(0),
                                                         MaxValueValidator(10),],
                                                         default=0,
                                                         null=True,
                                                         verbose_name='Оценка')
    
    student = models.ForeignKey(Student,
                               on_delete=models.CASCADE,
                               related_name='Grades',
                               verbose_name='Студент')
    
    course = models.ForeignKey(Course,
                               related_name='Course',
                               on_delete=models.CASCADE,
                               verbose_name='Курс')
    
    date = models.DateField(verbose_name='Дата оценки', null=True)

    date_add = models.DateField(auto_now_add=True,
                                null=True,
                                verbose_name='Дата добавления')
    
    date_update = models.DateField(auto_now=True,
                                   verbose_name='Дата изменения',
                                   null=True)
    
    class Meta:
        verbose_name = 'Оценка'
        verbose_name_plural = 'Оценки'