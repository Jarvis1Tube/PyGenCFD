MODULE VAR
   IMPLICIT NONE

   INTEGER, PARAMETER :: L1 = 62, M1 = 22
   REAL(8), PARAMETER :: eps = 1.D-8, alltime = 5.
   REAL(8), PARAMETER :: PI = 3.1415926535897932384626433832795
   INTEGER I, L2, J, M2, SOR_ITER
   REAL(8) TIME, DT, DX, XL, XLR, delT, delT1, RMAX, RET, DY, YL, YLR, AP0
   REAL(8) X(L1), XU(L1), YV(M1), Y(M1)
   REAL(8) T(L1, M1), T1(L1, M1), T0(L1, M1), RHO(L1, M1), GAMI(L1, M1), &
      CON(L1, M1), APS(L1, M1), AIP(L1, M1), AIM(L1, M1), AJM(L1, M1), AJP(L1, M1), &
      AP(L1, M1), GAMJ(L1, M1), B(L1, M1)

END MODULE VAR

!=============================================================================

MODULE USER
CONTAINS

   !-----------------------------------------------------------------------------

   {analytical_function}

   !-----------------------------------------------------------------------------

   SUBROUTINE START

      USE VAR
      XL = 0.; XLR = PI;
      YL = 0.; YLR = 1.;
      TIME = 0.; DT = 0.001;
      CALL GRID1(L1, L2, XL, XLR, XU, X)
      CALL GRID1(M1, M2, YL, YLR, YV, Y)

      DO J = 1, M1
         DO I = 1, L1
            T0(I, J) = Y(J)
            T(I, J) = T0(I, J)
         ENDDO
      ENDDO

      ! ГУ - 1го рода на правой границе
      DO J = 1, M1
         T(L1, J) = Y(J)
      ENDDO

   END SUBROUTINE START

   !-----------------------------------------------------------------------------

   SUBROUTINE GAMSOR

      USE VAR

      DO J = 2, M2
         DO I = 2, L2
            !В уравнении источник S = -1 необходимо проинтегрировать по контрольному объёму
            !Было: CON(I, J) = -0.5*(YV(I+1)**2 - YV(I)**2)*(XU(I+1) - XU(I))
            !      APS(I, J) = (XU(I+1) - XU(I)) * (YV(J+1) - YV(J))
            CON(I, J) = -0.5*(YV(J + 1)**2 - YV(J)**2)*(XU(I + 1) - XU(I)) + T(I, J)*(XU(I + 1) - XU(I))*(YV(J + 1) - YV(J))
            APS(I, J) = 0.0
            RHO(I, J) = 1.0
         ENDDO
      ENDDO

      !Определяем коэффициент теплопроводности kx на всех гранях ортогональных Ox,
      !в отличие от задачи 5.10, где kx определялся как среднее гармоническое только на внутренних гранях.
      !В цикле по I, для массива GAMI(I, J), перебираем номера всех граней,
      !а в цикле по J номера расчетных точек (номера контрольных объёмов)
      DO J = 2, M2
         DO I = 2, L1 !Было: DO I = 3, L2
            GAMI(I, J) = 1.0
         ENDDO
      ENDDO

      !Определяем коэффициент теплопроводности ky на всех гранях ортогональных Oy,
      !в отличие от задачи 5.10, где ky определялся как среднее гармоническое только на внутренних гранях.
      !В цикле по J, для массива GAMJ(I, J), перебираем номера всех граней,
      !а в цикле по I номера расчетных точек (номера контрольных объёмов)
      DO J = 2, M1  !Было: DO J = 3, M2
         DO I = 2, L2
            !Y-вая координата грани хранится в массиве YV
            GAMJ(I, J) = YV(J)*DSIN(X(I)) !Было: GAMJ(I, J) = Y(J)*SIN(X(I))
         ENDDO
      ENDDO

      ! ГУ - 2го рода на нижней границе
      !Фиксируя номер J = 2, перебираем I-ые номера контрольных объёмов прилегающих к нижней границе.
      DO I = 2, L2
         !Нумерация граней начинается с номера 2.
         GAMJ(I, 2) = 0.0
         !CON(I, 2) = CON(I, 2) - Y(1)*SIN(X(I))*(XU(I+1) - XU(I))
         !- это правильно, но лучше записать так:
         CON(I, 2) = CON(I, 2) - YV(2)*DSIN(X(I))*(XU(I + 1) - XU(I))
      ENDDO

      ! ГУ - 2го рода на верхней границе
      DO I = 2, L2
         GAMJ(I, M1) = 0.0
         !CON(I, M2) = CON(I, M2) + Y(M1)*SIN(X(I))*(XU(I+1)-XU(I))
         !- это правильно, но лучше записать так:
         CON(I, M2) = CON(I, M2) + YV(M1)*DSIN(X(I))*(XU(I + 1) - XU(I))
      ENDDO

      ! ГУ - 3го рода на левой границе
      DO J = 2, M2
         GAMI(2, J) = 0.0
         CON(2, J) = CON(2, J) - (TIME - Y(J)**4 + T(1, J)**4)*(YV(J + 1) - YV(J))
      ENDDO

      DO J = 1, M1
         T(1, J) = T(2, J) - (T0(1, J)**4 + TIME - Y(J)**4)*(X(2) - X(1))
      ENDDO

   END SUBROUTINE GAMSOR

   !-----------------------------------------------------------------------------

   SUBROUTINE OUTPUT

      USE VAR

      delT = 0.
      delT1 = 0.

      DO J = 2, M2
         DO I = 2, L2
            RET = FAN(X(I), Y(J), TIME)
            delT = DMAX1(delT, DABS(T(I, J) - RET))
            delT1 = DMAX1(delT1, 100.*DABS((T(I, J) - RET)/RET))
         ENDDO
      ENDDO

      WRITE (*, 1)
      WRITE (1, 1)

1     FORMAT(8X'TIME', 11X, 'T(5,5)', 10X, &
             'TAN(5,5)', 9X, 'delT', 12X, 'delT1')

      WRITE (*, 2) TIME, T(5, 5), FAN(X(5), Y(5), TIME), delT, delT1
      WRITE (1, 2) TIME, T(5, 5), FAN(X(5), Y(5), TIME), delT, delT1

2     FORMAT(1P5E16.6)

   END SUBROUTINE OUTPUT

   !-----------------------------------------------------------------------------
   SUBROUTINE ALLFILE

      USE VAR

      OPEN (UNIT=3, FILE='ALL.DAT', STATUS='UNKNOWN')

      WRITE (3, *) 'VARIABLES = "X","Y","T", "Ta","delT","delT1"'
      WRITE (3, *) 'ZONE I=10, J=10, F=POINT'

      DO J = 2, M2
         DO I = 2, L2
            RET = FAN(X(I), Y(J), TIME)
            WRITE (3, '(1P6E15.6)') X(I), Y(J), T(I, J), RET, DABS(T(I, J) - RET), &
               100.*DABS((T(I, J) - RET)/RET)

         ENDDO
      ENDDO

      ENDFILE 3
      CLOSE (3)

   END SUBROUTINE ALLFILE

END MODULE USER

!=============================================================================

PROGRAM COND2

   USE VAR
   USE USER

   OPEN (UNIT=1, FILE='Q2.OUT', STATUS='UNKNOWN')

   CALL START

   DO WHILE (TIME <= (alltime - 0.5*DT))
      TIME = TIME + DT
      RMAX = 1.

      DO WHILE (RMAX > eps)
         T1 = T
         CALL DIF
         CALL SOR
         CALL RT
      END DO

      CALL OUTPUT

      T0 = T

   END DO

   CALL ALLFILE

END PROGRAM COND2

!-----------------------------------------------------------------------------

SUBROUTINE GRID1(L1, L2, XL, XLR, XU, X)
   INTEGER L1, L2, I
   REAL(8) XL, XLR, XU(L1), X(L1), DX
   L2 = L1 - 1
   DX = XLR/DBLE(L1 - 2)
   XU(2) = XL

   DO I = 3, L1
      XU(I) = XU(I - 1) + DX
   ENDDO

   X(1) = XU(2)

   DO I = 2, L2
      X(I) = 0.5*(XU(I + 1) + XU(I))
   ENDDO

   X(L1) = XU(L1)

END SUBROUTINE GRID1

!-----------------------------------------------------------------------------

SUBROUTINE DIF

   USE VAR
   USE USER

   CALL GAMSOR

   DO J = 2, M2
      DO I = 2, L2
         AIM(I, J) = GAMI(I, J)*((YV(J + 1) - YV(J))/(X(I) - X(I - 1)))
         AIP(I, J) = GAMI(I + 1, J)*((YV(J + 1) - YV(J))/(X(I + 1) - X(I)))
         AJM(I, J) = GAMJ(I, J)*((XU(I + 1) - XU(I))/(Y(J) - Y(J - 1)))
         AJP(I, J) = GAMJ(I, J + 1)*((XU(I + 1) - XU(I))/(Y(J + 1) - Y(J)))
      ENDDO
   ENDDO

   DO J = 2, M2
      DO I = 2, L2
         AP0 = RHO(I, J)*(XU(I + 1) - XU(I))*(YV(J + 1) - YV(J))/DT
         AP(I, J) = -APS(I, J) + AIM(I, J) + AIP(I, J) &
                    + AJM(I, J) + AJP(I, J) + AP0
         B(I, J) = CON(I, J) + AP0*T0(I, J)
      ENDDO
   ENDDO

END SUBROUTINE DIF

!-----------------------------------------------------------------------------

SUBROUTINE SOR

   USE VAR
   DO J = 2, M2
      DO I = 2, L2
         T(I, J) = (AIM(I, J)*T(I - 1, J) + AIP(I, J)*T(I + 1, J) &
                    + AJM(I, J)*T(I, J - 1) + AJP(I, J)*T(I, J + 1) + B(I, J))/AP(I, J)

      ENDDO
   ENDDO

END SUBROUTINE SOR

!-----------------------------------------------------------------------------

SUBROUTINE RT

   USE VAR

   RMAX = 0.

   DO J = 2, M2
      DO I = 2, L2
         RMAX = DMAX1(RMAX, DABS(1.-T(I, J)/T1(I, J)))
      ENDDO
   ENDDO

   WRITE (*, *) RMAX
   WRITE (1, *) RMAX

END SUBROUTINE RT
