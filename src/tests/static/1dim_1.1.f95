MODULE VAR   ! Глобальные переменные доступны
   ! всем программным единицам, использующим
   ! данный модуль.
   IMPLICIT NONE
   INTEGER, PARAMETER :: L1 = 21
   REAL(8), PARAMETER :: eps = 1.D-4, alltime = 10.
   INTEGER I, L2
   REAL(8) TIME, DT, DX, XL, XLR, delT, &
           delT1, AP0, RMAX, RET
   REAL(8) X(L1), XU(L1)
   REAL(8) T(L1), T1(L1), T0(L1), &
           RHO(L1), GAMI(L1), CON(L1), APS(L1), AIP(L1), &
           AIM(L1), AP(L1), B(L1)
END MODULE VAR

!============================================

MODULE USER  ! Модуль содержит процедуры,
   ! которые изменяются при решении той или иной ! конкретной задачи, т.е.процедуры
   ! пользователя.
CONTAINS
   !--------------------------------------------
   ! generated !

   REAL*8 function FAN(x, t)
      implicit none
      REAL*8, intent(in) :: x
      REAL*8, intent(in) :: t

      REAL*8, parameter :: pi = 3.1415926535897932d0
      FAN = x / pi + 4 * exp(-9.0d0 * t) * sin(3.0d0 * x)

   end function

   ! generated !

   REAL*8 function INITIAL_CONDITION(x)
      implicit none
      REAL*8, intent(in) :: x

      REAL*8, parameter :: pi = 3.1415926535897932d0
      INITIAL_CONDITION = x / pi + 4 * sin(3.0d0 * x)

   end function

   ! generated !

   INTEGER*4 function L_X_CONDITION(t)
      implicit none
      REAL*8, intent(in) :: t

      L_X_CONDITION = 0

   end function

   ! generated !

   INTEGER*4 function R_X_CONDITION(t)
      implicit none
      REAL*8, intent(in) :: t

      R_X_CONDITION = 1

   end function

   !--------------------------------------------
   SUBROUTINE BOUND_INIT
      USE VAR

      ! ГУ-1го рода на левой стороне по оси X
      T(1) = L_X_CONDITION(TIME)

      ! ГУ-1го рода на правой стороне по оси X
      T(L1) = R_X_CONDITION(TIME)

   END SUBROUTINE BOUND_INIT

   SUBROUTINE START  ! Задаются параметры
      ! задачи, начальные условия и стационарные
      ! граничные условия первого рода.
      USE VAR
      XL = 0d0; XLR = 3.14159265358979d0
      CALL GRID(L1, L2, XL, XLR, XU, X)
      TIME = 0d0; DT = 0.1
      DO I = 1, L1
         T0(I) = INITIAL_CONDITION(X(I))
         T(I) = T0(I)
      END DO

   END SUBROUTINE START
   !--------------------------------------------
   SUBROUTINE GAMSOR   ! Задаются плотность,
      ! теплопроводность, источниковый член и
      ! граничные условия.
      USE VAR

      DO I = 2, L1
         GAMI(I) = 1.00000000000000
      END DO

      DO I = 2, L2
         CON(I) = 0.
         APS(I) = 0.
         RHO(I) = 1.
      END DO

   END SUBROUTINE GAMSOR
   !--------------------------------------------
   SUBROUTINE OUTPUT   ! Вывод данных в
      ! процессе расчета, вычисление ошибок.
      USE VAR

      delT = 0.
      delT1 = 0.
      DO I = 1, L1
         RET = DABS(T(I) - FAN(X(I), TIME))
         delT = DMAX1(delT, RET)
         delT1 = DMAX1(delT1, &
                 100. * RET / DABS(FAN(X(I), TIME)))
      END DO
      WRITE (*, 1)
      WRITE (1, 1)
      1     FORMAT(5X'TIME', 12X, 'T(5)', 12X, &
              'TAN(5)', 13X, 'delT', 13X, 'delT1')
      WRITE (*, 2) TIME, T(5), FAN(X(5), TIME), delT, delT1
      WRITE (1, 2) TIME, T(5), FAN(X(5), TIME), delT, delT1
      2     FORMAT(1P5E16.6)
   END SUBROUTINE OUTPUT
   !--------------------------------------------
   SUBROUTINE ALLFILE   ! Вывод результатов
      !  расчета в файл, для построения графиков.
      USE VAR
      OPEN (UNIT = 3, FILE = 'ALL.DAT', STATUS = 'UNKNOWN')
      WRITE (3, *) 'VARIABLES="X","T","Ta","delT", &
              "delT1"'
      WRITE (3, *) 'ZONE I=7, F=POINT'
      DO I = 1, L1
         RET = FAN(X(I), TIME)
         WRITE (3, '(1P5E15.6)') &
                 X(I), T(I), RET, DABS(T(I) - RET), &
                 100. * DABS((T(I) - RET) / RET)
      ENDDO
      ENDFILE 3
      CLOSE (3)
   END SUBROUTINE ALLFILE
END MODULE USER
!============================================
PROGRAM COND1   ! Программа численного
   ! решения начально-краевых задач для
   !одномерного уравнения теплопроводности.
   USE VAR
   USE USER
   OPEN (UNIT = 1, FILE = 'Q.OUT', STATUS = 'UNKNOWN')
   CALL START
   DO WHILE (TIME <= (alltime - 0.5 * DT))
      TIME = TIME + DT
      RMAX = 1.
      DO WHILE (RMAX > eps)
         CALL BOUND_INIT
         T1 = T
         CALL DIF
         CALL TDMA
         CALL RT
      END DO
      CALL OUTPUT
      T0 = T
   END DO
   CALL ALLFILE
END PROGRAM COND1
!============================================
SUBROUTINE GRID(L1, L2, XL, XLR, XU, X)
   ! Построение равномерной сетки
   INTEGER L1, L2, I
   REAL(8) XL, XLR, XU(L1), X(L1), DX
   L2 = L1 - 1
   DX = XLR / DBLE(L1 - 2)
   XU(2) = XL
   DO I = 3, L1
      XU(I) = XU(I - 1) + DX
   END DO
   X(1) = XU(2)
   DO I = 2, L2
      X(I) = 0.5 * (XU(I + 1) + XU(I))
   ENDDO
   X(L1) = XU(L1)
END SUBROUTINE GRID
!============================================
SUBROUTINE DIF   ! Расчет коэффициентов
   !                  дискретного аналога.
   USE VAR
   USE USER
   CALL GAMSOR
   DO I = 2, L2
      AIM(I) = GAMI(I) / (X(I) - X(I - 1))
      AIP(I) = GAMI(I + 1) / (X(I + 1) - X(I))
   ENDDO
   DO I = 2, L2
      AP0 = RHO(I) * (XU(I + 1) - XU(I)) / DT
      B(I) = CON(I) + AP0 * T0(I)
      AP(I) = -APS(I) + AP0 + AIM(I) + AIP(I)
   ENDDO
END SUBROUTINE DIF
!============================================
SUBROUTINE TDMA  ! Решение СЛАУ
   !                  методом прогонки.
   USE VAR
   REAL(8) DENOM, PT(L1), QT(L1)
   L2 = L1 - 1
   PT(1) = 0.
   QT(1) = T(1)
   DO I = 2, L2
      DENOM = AP(I) - PT(I - 1) * AIM(I)
      PT(I) = AIP(I) / (DENOM + 1.D-30)
      QT(I) = (B(I) + AIM(I) * QT(I - 1)) / &
              (DENOM + 1.E-30)
   ENDDO
   DO I = L2, 2, -1
      T(I) = T(I + 1) * PT(I) + QT(I)
   ENDDO
END SUBROUTINE TDMA
!============================================
SUBROUTINE RT   ! Вычисление параметра в критерии
   !   перехода на следующий временной слой
   USE VAR
   RMAX = 0.
   DO I = 2, L2
      RMAX = DMAX1(RMAX, DABS(1. - T(I) / T1(I)))
   ENDDO
   WRITE (*, *) RMAX
   WRITE (1, *) RMAX
END SUBROUTINE RT
