################################################################################################################################
############################## PROCESO DE TRATAMIENTO DE PDF + OCR TO JSON + JSON PARA BASE DE DATOS ###########################
################################################################################################################################

import os
import uuid
import cv2
import pytesseract
import logging
import fitz  # PyMuPDF
from PIL import Image
import numpy as np
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import InvoiceUploadSerializer
from voltix.models import Invoice
from django.http import JsonResponse

logger = logging.getLogger(__name__)

class InvoiceProcessView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(
        operation_summary="Subir y procesar facturas en PDF (OCR incluido)",
        operation_description=(
            "Permite a un usuario autenticado subir un archivo PDF, "
            "convertirlo en imágenes, procesarlas (escalado a grises) y ejecutar OCR para extraer texto."
        ),
        manual_parameters=[
            openapi.Parameter(
                name="file",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                description="El archivo PDF a subir y procesar.",
            ),
        ],
        responses={
            201: openapi.Response(
                description="Archivo procesado y texto extraído exitosamente.",
                examples={
                    "application/json": {
                        "status": "success",
                        "message": "Archivo procesado y texto extraído exitosamente.",
                        "extracted_text": "Texto extraído del archivo...",
                    }
                },
            ),
            400: openapi.Response(
                description="Error en la validación del archivo.",
                examples={
                    "application/json": {
                        "status": "error",
                        "details": {
                            "file": [
                                "This field is required.",
                                "File size exceeds 5 MB.",
                                "Invalid file type: application/msword. Only PDF files are allowed.",
                                "File extension does not match content type. Only '.pdf' files are allowed.",
                                "File name must end with '.pdf'."
                            ],
                        }
                    }
                },
            ),
            500: openapi.Response(
                description="Error durante el procesamiento.",
                examples={
                    "application/json": {
                        "status": "error",
                        "message": "Error durante el procesamiento.",
                        "details": "Detalles del error...",
                    }
                },
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = InvoiceUploadSerializer(data=request.data)
        if serializer.is_valid():
            try:
                uploaded_file = serializer.validated_data["file"]

                # Crear carpeta temporal si no existe
                temp_folder = settings.FILE_UPLOAD_TEMP_DIR or os.path.join(settings.BASE_DIR, "media", "temp")
                os.makedirs(temp_folder, exist_ok=True)

                # Guardar archivo temporalmente
                file_path = os.path.join(temp_folder, uploaded_file.name)
                with open(file_path, "wb+") as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)

                logger.info(f"Archivo '{uploaded_file.name}' subido exitosamente a {file_path}.")

                # Convertir PDF a imágenes
                images = self.pdf_to_images(file_path)
                processed_images = []

                # Procesar imágenes y guardar escala de grises
                for idx, img_data in enumerate(images):
                    grayscale_image = self.process_image(img_data)
                    processed_images.append(grayscale_image)

                # Realizar OCR en la primera imagen
                if processed_images:
                    ocr_text = self.perform_ocr(processed_images[0])  # Texto extraído
                    parsed_data = self.convert_ocr_to_json(ocr_text)  # Convertir OCR a JSON
                else:
                    ocr_text = "No se pudieron procesar las imágenes para OCR."
                    parsed_data = {}

                # Eliminar el archivo PDF subido
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Archivo PDF '{uploaded_file.name}' eliminado.")

                # Devolver el texto crudo del OCR y el JSON procesado
                return Response(
                    {
                        "status": "success",
                        "message": "Archivo procesado y texto extraído exitosamente.",
                        "ocr_text": ocr_text,  # Texto crudo capturado por OCR
                        "parsed_data": parsed_data,  # JSON estructurado a partir del texto OCR
                    },
                    status=status.HTTP_201_CREATED,
                )
            except Exception as e:
                logger.error(f"Error durante el procesamiento: {str(e)}")
                return Response(
                    {
                        "status": "error",
                        "message": "Error durante el procesamiento.",
                        "details": str(e),
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        logger.warning(f"Validación fallida: {serializer.errors}")
        return Response({"status": "error", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)




    def pdf_to_images(self, pdf_path):
        """
        Convierte un archivo PDF en imágenes (una por página).
        """
        images = []
        try:
            pdf_document = fitz.open(pdf_path)
            for page_number in range(len(pdf_document)):
                page = pdf_document[page_number]
                # pix = page.get_pixmap()
                ##########################################################
                zoom_x, zoom_y = 2.0, 2.0  # 2x scaling for higher DPI
                matrix = fitz.Matrix(zoom_x, zoom_y)
                pix = page.get_pixmap(matrix=matrix)
                #########################################################
                image_data = pix.tobytes("png")
                images.append(image_data)
            pdf_document.close()
            return images
        except Exception as e:
            logger.error(f"Error al convertir PDF a imágenes: {str(e)}")
            return []

    def process_image(self, image_data):
        """
        Convierte una imagen a escala de grises usando OpenCV.
        """
        try:
            np_array = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
            grayscale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # return grayscale_image
        #####################################################################
        # Increase contrast using CLAHE
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            contrast_image = clahe.apply(grayscale_image)

            # Remove noise
            denoised_image = cv2.fastNlMeansDenoising(contrast_image, None, 30, 7, 21)


        # Sharpen the image
            kernel = np.array([[0, -1, 0],
                           [-1, 5, -1],
                           [0, -1, 0]])
            sharpened_image = cv2.filter2D(denoised_image, -1, kernel)

            return sharpened_image
        except Exception as e:
            logger.error(f"Error during image preprocessing: {str(e)}")
            return None
##################################################################
    def perform_ocr(self, image):
        """
        Realiza OCR en una imagen usando Tesseract y retorna el texto extraído.
        """
        try:
            custom_oem_psm_config = r"--oem 3 --psm 11"
            pytesseract.pytesseract.tesseract_cmd = r"/usr/bin/tesseract"  # Ajustar según tu entorno

            # Convertir imagen OpenCV a imagen PIL
            pil_image = Image.fromarray(image)

            # Realiza la extracción de texto
            ocr_result = pytesseract.image_to_string(pil_image, lang="spa", config=custom_oem_psm_config)
        
            return ocr_result

        except Exception as e:
            logger.error(f"Error al realizar OCR: {str(e)}")
            return {"error": f"Error al procesar la imagen: {str(e)}"}

    def convert_ocr_to_json(self, ocr_text):
        """
        Convierte el texto OCR extraído a un JSON según la comercializadora detectada.
        """
        try:
            # Detectar la comercializadora en el texto OCR
            if "endesa" in ocr_text.lower():
                logger.info("Detectada la palabra clave 'endesa'. Ejecutando lógica de Endesa.")
                return self.extract_endesa_data(ocr_text)
            elif "iberdrola" in ocr_text.lower():
                logger.info("Detectada la palabra clave 'iberdrola'. Ejecutando lógica de Iberdrola.")
                return self.extract_iberdrola_data(ocr_text)
            else:
                logger.warning("No se detectó una comercializadora reconocida en el OCR.")
                return {
                    "error": "No se reconoció ninguna comercializadora en el OCR.",
                    "ocr_texto_completo": ocr_text
                }

        except Exception as e:
            logger.error(f"Error al convertir OCR a JSON: {str(e)}")
            return {"error": "Error al convertir OCR a JSON."}


    def extract_endesa_data(self, ocr_text):
        """
        Extrae los datos específicos de las facturas de Endesa a partir del texto OCR.
        """
        try:
            import re
            from datetime import datetime

            # Normalizar el texto para facilitar la búsqueda
            normalized_text = re.sub(r"\s+", " ", ocr_text)  # Reemplazar múltiples espacios o saltos de línea con un solo espacio

            # Lógica para extraer el nombre del cliente basado en el CIF y doble salto de línea
            def extract_nombre_cliente(text):
                """
                Extrae el nombre del cliente buscando el patrón después del CIF y dos saltos de línea.
                """
                match = re.search(r"CIF\s*[A-Za-z]\d{8}\s*\n\n(.+)", text, re.IGNORECASE)
                if match:
                    # Capturar lo que viene después del CIF y los saltos de línea
                    return match.group(1).strip().split("\n")[0]
                return None

            # Extraer el nombre del cliente
            nombre_cliente = extract_nombre_cliente(ocr_text)

            # Otros campos ya funcionales
            numero_referencia = re.search(r"Referencia:\s*([\w\/-]+)", normalized_text)
            fecha_emision = re.search(r"Fecha emisión factura:\s*(\d{2}/\d{2}/\d{4})", normalized_text)
            periodo_inicio = re.search(r"Periodo de facturación: del\s*(\d{2}/\d{2}/\d{4})", normalized_text)
            periodo_fin = re.search(r"a\s*(\d{2}/\d{2}/\d{4})", normalized_text)
            dias = re.search(r"\((\d+)\s*días\)", normalized_text)
            fecha_cargo_raw = re.search(r"Fecha de cargo:\s*(\d{2})\s*de\s*(\w+)\s*de\s*(\d{4})", normalized_text)
            mandato = re.search(r"Cod\.?Mandato:\s*(\w+)", normalized_text)
            costo_potencia = re.search(r"Potencia\s+([\d,\.]+)", normalized_text)
            costo_energia = re.search(r"Energía\s+([\d,\.]+)", normalized_text)
            descuentos = re.search(r"Descuentos\s+([\d,\.]+)", normalized_text)
            impuestos = re.search(r"Impuestos\s+([\d,\.]+)", normalized_text)
            total_a_pagar = re.search(r"Total\s+([\d,\.]+)", normalized_text)
            consumo_punta = re.search(r"Consumo punta\s+([\d,\.]+)\s*kWh", normalized_text, re.IGNORECASE)
            consumo_valle = re.search(r"Consumo valle\s+([\d,\.]+)\s*kW(?:n|h)", normalized_text, re.IGNORECASE)
            consumo_total = re.search(r"Consumo total\s+([\d,\.]+)\s*kWh", normalized_text, re.IGNORECASE)
            precio_efectivo_energia = re.search(r"ha salido a\s+([\d,\.]+)\s*€/kWh", normalized_text, re.IGNORECASE)

            # Convertir fechas al formato estándar (yyyy-mm-dd)
            def format_date(date_str):
                try:
                    return datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")
                except:
                    return None

            # Formatear la fecha de cargo si fue encontrada
            meses_es = {
                "enero": "01",
                "febrero": "02",
                "marzo": "03",
                "abril": "04",
                "mayo": "05",
                "junio": "06",
                "julio": "07",
                "agosto": "08",
                "septiembre": "09",
                "octubre": "10",
                "noviembre": "11",
                "diciembre": "12"
            }
            fecha_cargo = None
            if fecha_cargo_raw:
                dia, mes, anio = fecha_cargo_raw.groups()
                mes_numerico = meses_es.get(mes.lower())
                if mes_numerico:
                    fecha_cargo = f"{anio}-{mes_numerico}-{dia.zfill(2)}"

            # Construir JSON
            parsed_data = {
                "nombre_cliente": nombre_cliente,
                "numero_referencia": numero_referencia.group(1) if numero_referencia else None,
                "fecha_emision": format_date(fecha_emision.group(1)) if fecha_emision else None,
                "periodo_facturacion": {
                    "inicio": format_date(periodo_inicio.group(1)) if periodo_inicio else None,
                    "fin": format_date(periodo_fin.group(1)) if periodo_fin else None,
                    "dias": int(dias.group(1)) if dias else None,
                },
                "forma_pago": "Domiciliación bancaria",
                "fecha_cargo": fecha_cargo,
                "mandato": mandato.group(1) if mandato else None,
                "desglose_cargos": {
                    "costo_potencia": float(costo_potencia.group(1).replace(",", ".")) if costo_potencia else None,
                    "costo_energia": float(costo_energia.group(1).replace(",", ".")) if costo_energia else None,
                    "descuentos": float(descuentos.group(1).replace(",", ".")) if descuentos else None,
                    "impuestos": float(impuestos.group(1).replace(",", ".")) if impuestos else None,
                    "total_a_pagar": float(total_a_pagar.group(1).replace(",", ".")) if total_a_pagar else None,
                },
                "detalles_consumo": {
                    "consumo_punta": float(consumo_punta.group(1).replace(",", ".")) if consumo_punta else None,
                    "consumo_valle": float(consumo_valle.group(1).replace(",", ".")) if consumo_valle else None,
                    "consumo_total": float(consumo_total.group(1).replace(",", ".")) if consumo_total else None,
                    "precio_efectivo_energia": float(precio_efectivo_energia.group(1).replace(",", ".")) if precio_efectivo_energia else None,
                },
            }

            return parsed_data

        except Exception as e:
            logger.error(f"Error al convertir OCR a JSON: {str(e)}")
            return {"error": "Error al convertir OCR a JSON."}



    def extract_iberdrola_data(self, ocr_text):
        """
        Extrae y procesa los datos específicos de las facturas de Iberdrola.
        """
        import re
        from datetime import datetime

        normalized_text = re.sub(r"\s+", " ", ocr_text)

        # Lógica específica para Iberdrola
        nombre_cliente = re.search(r"Titular:\s*(.+)", normalized_text)
        numero_referencia = re.search(r"Número de contrato:\s*([\w\/-]+)", normalized_text)
        fecha_emision = re.search(r"Fecha de emisión:\s*(\d{2}/\d{2}/\d{4})", normalized_text)
        periodo_inicio = re.search(r"Periodo facturado: del\s*(\d{2}/\d{2}/\d{4})", normalized_text)
        periodo_fin = re.search(r"a\s*(\d{2}/\d{2}/\d{4})", normalized_text)

        # Convertir fechas
        def format_date(date_str):
            try:
                return datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")
            except:
                return None

        parsed_data = {
            "nombre_cliente": nombre_cliente.group(1) if nombre_cliente else None,
            "numero_referencia": numero_referencia.group(1) if numero_referencia else None,
            "fecha_emision": format_date(fecha_emision.group(1)) if fecha_emision else None,
            "periodo_facturacion": {
                "inicio": format_date(periodo_inicio.group(1)) if periodo_inicio else None,
                "fin": format_date(periodo_fin.group(1)) if periodo_fin else None,
            },
            "forma_pago": "Transferencia bancaria",
            "otros_campos_iberdrola": "Datos adicionales específicos de Iberdrola...",
        }

        return parsed_data



################################################################################################################################












    # def delete(self, request, *args, **kwargs):
    #     """
    #     Cleanup method to delete temporary files after processing.
    #     """
    #     file_name = request.data.get('file_name')
    #     if not file_name:
    #         logger.warning("File name not provided for deletion.")
    #         return Response({'status': 'error', 'message': 'File name not provided.'}, status=status.HTTP_400_BAD_REQUEST)

    #     file_path = os.path.join(TEMP_FOLDER, file_name)
    #     if os.path.exists(file_path):
    #         try:
    #             os.remove(file_path)
    #             logger.info(f"File '{file_name}' deleted successfully.")
    #             return Response({'status': 'success', 'message': 'File deleted successfully.'}, status=status.HTTP_200_OK)
    #         except Exception as e:
    #             logger.error(f"Error while deleting file '{file_name}': {str(e)}")
    #             return Response({
    #                 'status': 'error',
    #                 'message': 'An error occurred while deleting the file.',
    #                 'details': str(e)
    #             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    #     else:
    #         logger.warning(f"File '{file_name}' not found for deletion.")
    #         return Response({'status': 'error', 'message': 'File not found.'}, status=status.HTTP_404_NOT_FOUND)



################################################################################################################################
############################################ GET - VISUALIZAR FATURA POR ID ####################################################
################################################################################################################################

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import InvoiceSerializer
from voltix.models import Invoice

class InvoiceDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Obtener factura por ID",
        operation_description="Permite a un usuario autenticado obtener los detalles de una factura específica por su ID.",
        responses={
            200: openapi.Response(
                description="Detalles de la factura obtenidos exitosamente.",
                examples={
                    "application/json": {
                        "id": 123,
                        "user": {"id": 1, "username": "usuario"},
                        "billing_period_start": "2023-01-01",
                        "billing_period_end": "2023-01-31",
                        "data": {
                            "nombre_cliente": "Ejemplo Cliente",
                            "detalles_consumo": {
                                "consumo_punta": 120.5,
                                "consumo_valle": 85.4,
                                "total_kwh": 205.9
                            }
                        }
                    }
                },
            ),
            404: openapi.Response(
                description="Factura no encontrada.",
                examples={
                    "application/json": {
                        "detail": "Factura no encontrada."
                    }
                },
            ),
            401: openapi.Response(
                description="No autenticado.",
                examples={
                    "application/json": {
                        "detail": "No se han proporcionado credenciales de autenticación."
                    }
                },
            ),
        },
    )
    def get(self, request, invoice_id):
        invoice = get_object_or_404(Invoice, pk=invoice_id)
        serializer = InvoiceSerializer(invoice)
        return Response(serializer.data, status=status.HTTP_200_OK)

################################################################################################################################