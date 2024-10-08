from odoo import models, api, fields, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta






class CustomPopMessage(models.TransientModel):
    _name = "custom.pop.message"
    _description = "Registers advices with the operations of electronic documents."

    name = fields.Text('Mensaje', readonly=True)

    def messagebox(self,advices):
        return {
            'name': 'Theos - Aviso',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'custom.pop.message',
                'target':'new',
                'context':{'default_name': advices}
                }


class SriDocumentoElectronicoImport(models.Model):
    _name = 'l10n_ec_base.edoc.import'
    _description ='Documentos electrónicos a importar'

    @api.model
    def create(self, vals):
        res = super(SriDocumentoElectronicoImport, self).create(vals)
        print(res)

        res.get_doc()
        return res

    def exist_same_name(self,name):
        domain=[('autorizacion','=',name)]
        hay = self.env['l10n_ec_base.edoc.import'].search(domain)
        estan = hay-self
        data = (estan and estan[0]) or False
        print('HAY= ',hay,'   estan=',estan,'  data=',data)

        return data

    def action_view_purchase_order(self):
        '''
        This function returns an action that display existing vendor bills of given purchase order ids.
        When only one found, show the vendor bill immediately.
        '''
        action = self.env.ref('purchase.purchase_form_action')
        result = action.read()[0]

        #override the context to get rid of the default filtering
        result['context'] = {'type': 'in_invoice', 'default_purchase_id': self.id}

        if not self.orders_purchase_ids:
            # Choose a default account journal in the same currency in case a new invoice is created
            journal_domain = [
                ('type', '=', 'purchase'),
                ('company_id', '=', self.company_id.id),
                ('currency_id', '=', self.currency_id.id),
            ]
            default_journal_id = self.env['account.journal'].search(journal_domain, limit=1)
            if default_journal_id:
                result['context']['default_journal_id'] = default_journal_id.id
        #else:
        #    # Use the same account journal than a previous invoice
        #    result['context']['default_journal_id'] = self.invoice_ids[0].journal_id.id

        #choose the view_mode accordingly
        if len(self.orders_purchase_ids) != 1:
            result['domain'] = "[('id', 'in', " + str(self.orders_purchase_ids.ids) + ")]"
        elif len(self.orders_purchase_ids) == 1:
            res = self.env.ref('purchase.purchase_order_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = self.orders_purchase_ids.id
        #result['context']['default_origin'] = self.name
        #result['context']['default_reference'] = self.partner_ref
        return result


    def action_view_invoice(self):
        '''
        This function returns an action that display existing vendor bills of given purchase order ids.
        When only one found, show the vendor bill immediately.
        '''
        action = self.env.ref('account.action_move_in_invoice_type')
        result = action.read()[0]
        create_bill = self.env.context.get('create_bill', False)
        # override the context to get rid of the default filtering
        result['context'] = {
            'default_type': 'in_invoice',
            'default_company_id': self.company_id.id,
            'default_purchase_id': self.id,
        }
        # choose the view_mode accordingly
        if len(self.invoices_purchase_ids) > 1 and not create_bill:
            result['domain'] = "[('id', 'in', " + str(self.invoices_purchase_ids.ids) + ")]"
        else:
            res = self.env.ref('account.view_move_form', False)
            form_view = [(res and res.id or False, 'form')]
            if 'views' in result:
                result['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                result['views'] = form_view
            # Do not set an invoice_id if we want to create a new bill.
            if not create_bill:
                result['res_id'] = self.invoices_purchase_ids.id or False
        #result['context']['default_edoc_import_id'] = self.id
        #result['context']['default_ref'] = self.partner_ref
        return result

    def action_view_invoice_old(self):
        '''
        This function returns an action that display existing vendor bills of given purchase order ids.
        When only one found, show the vendor bill immediately.
        '''
        action = self.env.ref('purchase.purchase_form_action')
        result = action.read()[0]

        #override the context to get rid of the default filtering
        result['context'] = {'type': 'in_invoice', 'default_purchase_id': self.id}

        if not self.orders_purchase_ids:
            # Choose a default account journal in the same currency in case a new invoice is created
            journal_domain = [
                ('type', '=', 'purchase'),
                ('company_id', '=', self.company_id.id),
                ('currency_id', '=', self.currency_id.id),
            ]
            default_journal_id = self.env['account.journal'].search(journal_domain, limit=1)
            if default_journal_id:
                result['context']['default_journal_id'] = default_journal_id.id
        #else:
        #    # Use the same account journal than a previous invoice
        #    result['context']['default_journal_id'] = self.invoice_ids[0].journal_id.id

        #choose the view_mode accordingly
        if len(self.orders_purchase_ids) != 1:
            result['domain'] = "[('id', 'in', " + str(self.orders_purchase_ids.ids) + ")]"
        elif len(self.orders_purchase_ids) == 1:
            res = self.env.ref('purchase.purchase_order_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = self.orders_purchase_ids.id
        #result['context']['default_origin'] = self.name
        #result['context']['default_reference'] = self.partner_ref
        return result

    @api.model
    def _default_currency(self):
        return self.env.user.company_id.currency_id

    @api.model
    def _default_ambiente_id(self):
        #return self.env.user.company_id.ambiente_id
        return self.env.ref('l10n_ec_base_ece.produccion')


    @api.model
    def _default_tipo_homologacion(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        tipo_homologacion = ICPSudo.get_param('l10n_ec_base.tipo_homologacion', default='manual')
        # print("tipo_homologacion >> ",tipo_homologacion)
        return tipo_homologacion

    @api.model
    def _default_state_purchase_orders(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        state_purchase_orders = ICPSudo.get_param('state_purchase_orders', default='done')
        print("state_purchase_orders >> ",state_purchase_orders)
        return state_purchase_orders



    @api.onchange('data_filename')
    def _onchange_data_filename(self):
        self.name = self.data_filename[:4]


    currency_id = fields.Many2one('res.currency', string='Currency',
        required=True, readonly=True,
        default=_default_currency)

    reference = fields.Char(string='Nro de Documento')
    invoice_date = fields.Date(string='Fecha del Documento')
    partner_id = fields.Many2one('res.partner', string='Entidad', change_default=True)

    email = fields.Char(string='Correo Electrónico' ,related='partner_id.email', store=True)

    comprobante_id = fields.Many2one(
        'l10n_ec_base.comprobante', string='Comprobante', copy=False)
    fechaautorizacion = fields.Datetime('Fecha y hora de autorización', )
    establecimiento = fields.Char('Establecimiento', copy=False, size=3, )
    puntoemision = fields.Char('Punto de emisión', copy=False, size=3, )
    autorizacion = fields.Char('Autorización', copy=False, )
    secuencial = fields.Char(
        string='Secuencial', copy=False, index=True,
        help="En caso de no tener secuencia, debe ingresar nueves, ejemplo: 999999.", )

    # Campos informativos del SRI.
    basenograiva = fields.Monetary(string="Subtotal no grava I.V.A.",copy=True, )
    baseimponible = fields.Monetary(string="Subtotal I.V.A. 0%", copy=True, )
    baseimpgrav = fields.Monetary(string="Subtotal gravado con I.V.A.", copy=True, )
    baseimpexe = fields.Monetary(string="Subtotal excento de I.V.A.", copy=True, )
    montoiva = fields.Monetary(string="Monto I.V.A", copy=True, )
    montoice = fields.Monetary(string="Monto I.c.e.", copy=True, )

    # Otros campos informativos de uso interno.
    # No se usa los campos propios de Flectra porque estos restan las retenciones.
    total = fields.Monetary(string='TOTAL', default=0.0, copy=True, )
    subtotal = fields.Monetary(string='SUBTOTAL',copy=True, )
    total_descuento = fields.Monetary(string='Total Descuento' ,default=0.0, copy=True)
    porcentaje_descuento = fields.Monetary(string='Porcentaje Descuento' ,compute='_calculate_discount')
    total_descuento_lineas = fields.Monetary(string='Descuento Lineas' ,compute='_calculate_discount_lineas')

    @api.depends('total_descuento','total','subtotal','total_descuento_lineas')
    def _calculate_discount(self):
        for order in self:
            if order.total_descuento_lineas==0.0:
                if len(order.compra_detail_ids)>0:
                    discount = (order.total_descuento / (order.subtotal)) * 100 if order.total_descuento !=0 else 0.0
                else:
                    discount = 0.0
            else:
                if len(order.compra_detail_ids)>0:
                    discount = (order.total_descuento / (order.subtotal+order.total_descuento)) * 100 if order.total_descuento !=0 else 0.0

                else:
                    discount = 0.0
            order.porcentaje_descuento = discount



    @api.depends('compra_detail_ids.price_unit','compra_detail_ids.monto_discount','compra_detail_ids.discount')
    def _calculate_discount_lineas(self):
        for order in self:
            discount= sum(order.compra_detail_ids.mapped('monto_discount')) or 0.0
            order.total_descuento_lineas = discount


    compra_detail_ids = fields.One2many('l10n_ec_base.edoc.import.details', 'compra_id', string='Mapeo de Compra')
    detail_ids = fields.Many2many('l10n_ec_base.edoc.import.details',string='Lineas')

    estado_sri = fields.Selection([
        ('NO ENVIADO', 'NO ENVIADO'),  # Documentos fuera de línea.
        ('RECIBIDA', 'RECIBIDA'),
        ('EN PROCESO', 'EN PROCESO'),
        ('DEVUELTA', 'DEVUELTA'),
        ('AUTORIZADO', 'AUTORIZADO'),
        ('NO AUTORIZADO', 'NO AUTORIZADO'),
        ('RECHAZADA', 'RECHAZADA'),
    ])

    name = fields.Char('Clave de acceso', )
    fecha = fields.Datetime(string='Fecha', readonly=True, index=True,copy=False, default=datetime.now())
    fecha_proceso = fields.Datetime('Fecha procesado', readonly=True, )
    mensajes = fields.Text('Mensajes', )
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    user_id = fields.Many2one('res.users', string='Usuario', index=True, default=lambda self: self.env.user)
    estatus_cola = fields.Selection([
        ('creado', 'DOCUMENTO SIN PROCESAR'),  # Documentos fuera de línea.
        ('procesando', 'DOCUMENTO SE ESTA PROCESANDO'),
        ('procesado', 'DOCUMENTO PROCESADO'),
    ], string='Estado de Cola',default='creado', readonly=True,)
    estatus_import = fields.Selection([
        ('NONE', 'NO IMPORTADO'),
        ('GET', 'ARCHIVO XML DESCARGADO'),
        ('IMPORT', 'IMPORTADO'),
        ('MAPPING', 'EN HOMOLOGACION'),
        ('ORDER', 'ORDEN DE COMPRA GENERADA'),
        ('INVOICE', 'FACTURA DE COMPRA GENERADA'),
        ('FAIL GET', 'ERROR DE COMUNICACION SRI'),
        ('FAIL READ', 'ERROR DE IMPORTACION XML'),
        ('FAIL PRODUCTS', 'ERROR DE HOMOLOGACION'),
    ], string='Estado',default='NONE',)
    tipo_importacion= fields.Selection(
        [
            ('sri', 'Desde el SRI'),
            ('file', 'Desde Archivo')
            ],
        'Tipo de importación',default='sri')
    tipo_homologacion = fields.Selection(
        [
            ('auto', 'Homologación automática'),
            ('manual', 'Homologación manual')
            ],
        'Tipo de Homologación', default = _default_tipo_homologacion)

    state_purchase_orders = fields.Selection(
        [
            ('draft', 'En borrador'),
            ('done', 'Procesar')
            ],
        'Estado de Ordenes de Compras',default=_default_state_purchase_orders)

    pagina = fields.Integer('Pagina', default =1, readonly=True)
    pagina_desc = fields.Selection(
        [
            ('1', 'Carga de Datos'),
            ('2', 'Homologación'),
            ('3', 'Revisión'),
            #('4', 'Retención')
        ],
        string='Proceso de Importación',required=True,default='1'
    )

    data_filename = fields.Char('Documento XML - Nombre',size=256)
    data_file = fields.Binary(string='Archivo Documento XML')
    products_to_map_count = fields.Integer(compute='_products_to_map_count', string='# Productos a Homologar')
    orders_purchase_ids = fields.One2many('purchase.order', 'edoc_import_id', string='Ordenes de Compra Generadas')
    orders_to_map_count = fields.Integer(compute='_orders_to_map_count', string='# Ordenes Creadas')

    invoices_purchase_ids = fields.One2many('account.move', 'edoc_import_id', string='Facturas de Compra Generadas')
    invoices_to_map_count = fields.Integer(compute='_invoices_to_map_count', string='# Facturas Creadas')
    storables_to_map_count = fields.Integer(compute='_storables_to_map_count', string='# Almacenables a Homologar')

    ambiente_id = fields.Many2one(
        'l10n_ec_base.ambiente', string='Ambiente', default = _default_ambiente_id)

    product_id = fields.Many2one('product.product', string='Producto', domain=[('purchase_ok', '=', True)])

    # _sql_constraints = [
    #     ('name_uniq', 'unique(name, company_id)', 'La clave de acceso debe ser unica!!!'),
    # ]

    @api.depends('compra_detail_ids.price_unit', 'total', 'total_descuento')
    def _storables_to_map_count(self):
        storables_to_map_count=0
        for mlinea  in self.compra_detail_ids:
            if mlinea.type=='product':
                storables_to_map_count += 1
        self.storables_to_map_count = storables_to_map_count


    @api.depends('compra_detail_ids.price_unit', 'total', 'total_descuento')
    def _products_to_map_count(self):
        products_to_map_count=0
        for mlinea  in self.compra_detail_ids:
            if not mlinea.product_tmpl_id:
                products_to_map_count += 1
        self.products_to_map_count=products_to_map_count

    @api.depends('compra_detail_ids.price_unit', 'total', 'total_descuento')
    def _orders_to_map_count(self):
        orders_to_map_count=0
        for mlinea  in self.orders_purchase_ids:
            if not mlinea.state=='cancel':
                orders_to_map_count += 1
        self.orders_to_map_count = orders_to_map_count

    @api.depends('compra_detail_ids.price_unit', 'total', 'total_descuento')
    def _invoices_to_map_count(self):
        invoices_to_map_count=0
        for invoice  in self.invoices_purchase_ids:
            if not invoice.state=='cancel':
                invoices_to_map_count += 1
        self.orders_to_map_count = invoices_to_map_count

    def normalize_date_to_odoo(self, date):
        if not date:
            return
        res = datetime.strptime(date, '%d/%m/%Y').strftime( '%Y-%m-%d')
        return res


    def normalize_datetime_to_odoo(self, date):
        if not date:
            return
        try:
            try:
                res = datetime.strptime(date[:19], '%d/%m/%Y %H:%M:%S').strftime( '%Y-%m-%d  %H:%M:%S')
            except Exception as e:
                res = datetime.strptime(date[:19], '%Y-%m-%d %H:%M:%S').strftime( '%Y-%m-%d  %H:%M:%S')
        except Exception as ex:
            date = list(date.values())[1]
            res = datetime.strptime(date[:19], '%Y-%m-%dT%H:%M:%S').strftime( '%Y-%m-%d  %H:%M:%S')

        return res


    def read_xml(self,file_to_open):
        filename = pathlib.Path(file_to_open)
        if not filename.exists():
            return None
        else:
            f = open(file_to_open)
            mf= f.read()
            return mf



    def save_xml(self, xml_element,file_to_write):
        try:
            dir = os.path.dirname(file_to_write)
            pathlib.Path(dir).mkdir(parents=True, exist_ok=True)
            filew = open(file_to_write,'w+')
            filew.write(xml_element)
            filew.close()
        except:
            return False
        return True

    def create_proveedor(self, infoTributaria,email):
        vals_prov = {}
        table_obj = self.env['res.partner']
        mrecord = None
        mrecord = table_obj.search([('vat','=',infoTributaria['ruc'])], limit=1)
        if not mrecord:
            vals_prov['name']=str(infoTributaria["razonSocial"]).upper()
            if ("S.A." in str(infoTributaria["razonSocial"]).upper()) or (" C.A." in str(infoTributaria["razonSocial"]).upper()):
                vals_prov['property_account_position_id']=self.env.ref('l10n_ec_base.fiscal_position_sociedad')

            vals_prov['vat']=infoTributaria['ruc']
            #vals_prov['type_identifier']='ruc'
            #vals_prov['tipo_persona']='0'
            #vals_prov['is_company']=0
            vals_prov['customer_rank']=1
            vals_prov['supplier_rank']=1
            vals_prov['street']=infoTributaria["dirMatriz"]
            #if email:
            #    vals_prov['email']=email
            vals_prov['email']=email
            #vals_prov['phone']="0000"
            #vals_prov['type']="contact"
            vals_prov['property_payment_term_id']=self.env.ref('account.account_payment_term_immediate')
            vals_prov['property_supplier_payment_term_id']=self.env.ref('account.account_payment_term_immediate')
            #print (vals_prov)
            mrecord = table_obj.create(vals_prov)
        #else:
        #    if not mrecord.email:
        #        if email:
        #            vals_prov['email']=email
        #            mrecord.update(vals)
        return mrecord


    def _prepare_import_line_from_xml(self, line, partner):
        codes = None
        codes = self.env['product.supplierinfo'].search([
            ('name', '=', partner.id),
            ('product_code', '=', line['codigoPrincipal'])
            ], limit=1)
        por_descuento=0.0
        product = None
        template = None
        unificar = False
        distribuir = False
        distribuir_code = ''
        if codes:
            product = codes.product_id
            template = codes.product_tmpl_id
            unificar  = codes.unificar
            distribuir = codes.distribuir
            distribuir_code = codes.distribuir_code
        try:
            por_descuento= (float(line['descuento'])/(float(line['precioUnitario'])*float(line['cantidad'])))*100
        except Exception as e:
            por_descuento = 0.00


        data ={
            'compra_id': self.id,
            'product_name':line['descripcion'],
            'product_code':line['codigoPrincipal'],
            'product_qty':line['cantidad'],
            'type':'product',
            'price_unit':line['precioUnitario'],
            'monto_discount':line['descuento'],
            'total_sin_impuesto':line['precioTotalSinImpuesto'],
            'unitario_sin_impuesto':float(line['precioTotalSinImpuesto'])/float(line['cantidad']),
            'discount':por_descuento,
            'pvp_empaque':float(line['precioUnitario'])*1.20,
            'unificar':unificar,
            'distribuir':distribuir,
            'distribuir_code':distribuir_code,
        }

        if template:
            data['product_tmpl_id']=template.id
            data['product_uom']=template.uom_po_id.id
            data['pvp_empaque'] = template.list_price
            data['categ_id'] = template.categ_id.id
            data['type'] = template.type
            data['product_id']=product.id if product else template.id
            data['tracking'] = template.tracking
            supplier_taxes_id = template.supplier_taxes_id.ids
            taxes_id = template.taxes_id.ids
            data['supplier_taxes_id']=[( 6, 0, template.supplier_taxes_id.ids)]
            data['customer_taxes_id']=[( 6, 0, template.taxes_id.ids)]

        else:
            data['crear'] = False #True Estaba antes, ahora es manual
            taxes =[]
            taxes_sale =[]
            mis_impuestos=None
            try:
                mis_impuestos=[line['impuestos']['impuesto']]
            except:
                mis_impuestos=None

            # if mis_impuestos:
            #     lista_mpuestos = json.loads(json.dumps(mis_impuestos))
            #     for impuesto in lista_mpuestos:
            #         print(impuesto)
            #         table_obj = self.env['account.tax']
            #         mrecord = None
            #         mrecord = table_obj.search([
            #             ('codigo','=',impuesto['codigo']),
            #             ('codigoporcentaje','=',impuesto['codigoPorcentaje']),
            #             ], limit=1)
            #         if mrecord:
            #             data['supplier_taxes_id']=[( 6, 0, mrecord.ids)]
                #data['impuestos']=lista_mpuestos
                #self._prepare_import_line_taxes_from_xml(lista_mpuestos)
        return data



    def get_de_from_xml(self, xml):
        """
        :param xml:
        :return:
        """

        autorizacion_dict = xmltodict.parse(xml)['autorizacion']
        estado = autorizacion_dict['estado']
        comprobante = autorizacion_dict['comprobante'].encode('utf-8')
        comprobante = xmltodict.parse(comprobante)
        inv_obj = self.env['account.move']
        if 'factura' in comprobante.keys():
            infoTributaria = comprobante['factura']['infoTributaria']
            infoFactura = comprobante['factura']['infoFactura']
            key = 'factura'

            fecha = infoFactura['fechaEmision']
            vat = infoFactura['identificacionComprador']
            #partner = self.env['res.partner'].search([('vat', '=', vat)], limit=1)
            _email = self.email
            if not _email:
                _email='uno@uno.com'

            partner= self.create_proveedor(infoTributaria, _email)


            detalle = comprobante['factura']['detalles']['detalle']

            try:
                m=detalle['codigoPrincipal']
                _una_sola_linea = True
            except:
                _una_sola_linea = False
                #info_lineas['detalle']=[info_lineas['detalle']]


            if _una_sola_linea:
                detalle=[comprobante['factura']['detalles']['detalle']]


            supplier = self.env['product.supplierinfo']
            supplier = supplier.search([('name', '=', partner.id)])

            secuencial = infoTributaria['secuencial']

            inv = inv_obj.search([('secuencial', '=', secuencial)])

            try:
                info_pagos =infoFactura['pagos']['pago']
                fpago_code = info_pagos['formaPago']
            except:
                fpago_code = '01'


            forma_pago_id= self.env['l10n_ec_base.formapago'].search(
                 [('code', '=', fpago_code)], limit=1).id


            ICPSudo = self.env['ir.config_parameter'].sudo()
            product_categ_id = literal_eval(ICPSudo.get_param('product_categ_id', default='False'))
            context = self.env.context.copy()
            #print('product_categ_id>>>>> ',product_categ_id)
            if product_categ_id:
                context.update( { 'product_categ_id': product_categ_id,'default_product_categ_id':product_categ_id } )

            #if self._context.get('product_categ_id') or self._context.get('default_product_categ_id'):
            #    return self._context.get('product_categ_id') or self._context.get('default_product_categ_id')
            for mdetail  in self.compra_detail_ids:
                mdetail.unlink()

            lines = []

            for linea in detalle:
                data=self._prepare_import_line_from_xml(linea,partner)
                if not 'categ_id' in data:
                    data['categ_id']=product_categ_id
                lines.append((0,0, data))

            try:
                fechaauto = autorizacion_dict['fechaAutorizacion']
            except Exception as e:
                fechaauto = list(autorizacion_dict['fechaAutorizacion'].values())

            inv_dict = {
                'comprobante_id': self.env['l10n_ec_base.comprobante'].search(
                 [('code', '=', infoTributaria['codDoc'])], limit=1).id,
                #'epayment_id': forma_pago_id,
                'secuencial': infoTributaria['secuencial'],
                'partner_id': partner.id,
                'invoice_date': self.normalize_date_to_odoo(fecha),
                'establecimiento': infoTributaria['estab'],
                'puntoemision': infoTributaria['ptoEmi'],
                'autorizacion': autorizacion_dict['numeroAutorizacion'],
                'name':infoTributaria['claveAcceso'],
                'fechaautorizacion' : self.normalize_datetime_to_odoo(fechaauto),
                'estado_sri':  autorizacion_dict['estado'],
                'subtotal' : infoFactura['totalSinImpuestos'] or 0.0,
                'total' : infoFactura['importeTotal'] or 0.0,
                'total_descuento' : infoFactura['totalDescuento'] or 0.0,
                'reference':infoTributaria['estab']+'-'+infoTributaria['ptoEmi']+'-'+infoTributaria['secuencial'],
                'compra_detail_ids': lines,

                }

        elif 'comprobanteRetencion' in comprobante.keys():
            infoTributaria = comprobante['comprobanteRetencion']['infoTributaria']
            key = 'comprobanteRetencion'
            fecha = comprobante['comprobanteRetencion']['infoCompRetencion']['fechaEmision']

            inv_obj = self.env['account.move']
            docs = []

            for impuesto in comprobante['comprobanteRetencion']['impuestos']['impuesto']:
                if impuesto['numDocSustento'] not in docs:
                    docs.append(impuesto['numDocSustento'])

            for d in docs:
                establecimiento = d[:3]
                ptoemision = d[3:6]
                secuencial = d[6:].lstrip('+-0')
                inv += inv_obj.search([('establecimiento','=',establecimiento),
                                     ('puntoemision','=',ptoemision),
                                     ('secuencial','=',secuencial)])

            fecha = comprobante['comprobanteRetencion']['infoCompRetencion']['fechaEmision']

            inv_dict = {
                'r_comprobante_id': self.env['l10n_ec_base.comprobante'].search(
                [('code', '=', infoTributaria['codDoc'])], limit=1).id,
                'fechaemiret1': self.normalize_date_to_odoo(fecha),
                'estabretencion1': infoTributaria['estab'],
                'ptoemiretencion1': infoTributaria['ptoEmi'],
                'autretencion1': autorizacion_dict['numeroAutorizacion'],
                'secretencion1': infoTributaria['secuencial'],
                }

        elif 'guiaRemision' in comprobante.keys():
            infoTributaria = comprobante['guiaRemision']['infoTributaria']
            key = 'guiaRemision'



        autorizacion = {
                'fechaautorizacion' : autorizacion_dict['fechaAutorizacion'],
                'estado_sri':  autorizacion_dict['estado'],
                'autorizacion' : autorizacion_dict['numeroAutorizacion']
        }
        return  key, infoTributaria, autorizacion, inv_dict, inv, secuencial


    def register_de_data(self, xml, list_msg):
        key, info, autorizacion, xml_data, ces, secuencial = self.get_de_from_xml(xml)

        if (autorizacion['estado_sri']!='AUTORIZADO'):
            raise UserError("El documento no esta autorizado. Estado en el xml: "+autorizacion['estado_sri'])
        self.write(xml_data)


        for mlinea  in self.compra_detail_ids:
            mlinea._onchange_type()
        self.write({
                    'estatus_import':'IMPORT',
                    'fecha_proceso':datetime.now(),
                    'mensajes':'',
                    })



    def get_doc_file(self,type, path_file):
        self.ensure_one()
        for obj in self:
            if type=='file':
                if not self.data_file:
                    raise UserError("Necesita seleccionar un Archivo XML")
                    continue

                directory = os.path.normpath(os.path.normcase(config['path_electronic_import']))
                pathlib.Path(directory).mkdir(parents=True, exist_ok=True)
                file_to_write = os.path.normpath(os.path.normcase(os.path.join(directory,obj.data_filename)))
                filew = open(file_to_write,'wb+')
                filew.write(base64.b64decode(self.data_file))
                filew.close()
                auth= obj.read_xml(file_to_write)
            else:
                if not os.path.exists(path_file):
                    raise UserError("Necesita seleccionar un Archivo XML")
                    continue
                auth= obj.read_xml(path_file)

            if auth == None:
                raise UserError("Necesita seleccionar un Archivo XML")
                continue
            estado_sri=''
            list_msg=[]

            if 'xml' in auth:
                obj.register_de_data(auth, list_msg)
                if obj.tipo_homologacion=='auto':
                    #obj._revisar_duplicado()
                    self.homologar_lineas_importadas()
            else:
                raise UserError(_("Error: Ingrese un archivo xml valido."))
            msg_obj = self.env['custom.pop.message']
            advices = ''
            list_msg = list(set(list_msg))
            if list_msg:
                for msg in list_msg:
                    advices += msg+'\n'
                return msg_obj.messagebox(advices)



    def get_doc(self):
        path_file = os.path.normpath(os.path.normcase(os.path.join(config['path_electronic_import'],"sri")))
        doc_existe = self.exist_same_name(self.name)
        print(doc_existe)
        if doc_existe:

            msn="Ya existe un documento importado con esta clave de acceso:\nAutorizacion: %s\nEntidad: %s\nFactura: %s-%s-%s\nFecha: %s\nValor: $ %s"%(doc_existe.name,doc_existe.partner_id.name,doc_existe.establecimiento,doc_existe.puntoemision,doc_existe.secuencial, doc_existe.invoice_date,doc_existe.total)
            raise UserError(msn)


        self.write({
                    'estatus_cola':'procesando',
                    'fecha_proceso':datetime.now()
                    })
        if self.tipo_importacion=='sri':
            if not self.name:
                raise UserError(_("Dede ingresar la clave de acceso para continuar!"))
            #return self.get_doc_sri(path_file)
            self.get_doc_sri(path_file)
        if self.tipo_importacion=='file':
            return self.get_doc_file(type='file',path_file=None)


    def get_doc_sri(self, path_file):
        for obj in self:
            if not len(str(obj.name)) ==49:
                raise UserError("El nro de autorización debe ser de 49 caracteres")
                continue

            claveacceso = self.name
            name_file = '{0}.xml'.format(claveacceso)
            file_tmp = os.path.normpath(os.path.normcase(os.path.join(path_file,name_file)))

            if os.path.exists(file_tmp):
                print("LEEE LOCAL")
                self.get_doc_file(type='tmp',path_file=file_tmp)
            else:
                print("carga desde el SRI")
                if self.receive_de_offline(file_tmp):
                    self.get_doc_file(type='tmp',path_file=file_tmp)
            #return {
            #        "type": "ir.actions.do_nothing",
            #    }


    def receive_de_offline(self, file_tmp):
        ambiente_id = self.ambiente_id #self.env.user.company_id.ambiente_id
        claveacceso = self.name
        try:
            client = Client(ambiente_id.autorizacioncomprobantes)
            with client.settings(raw_response=False):
                response = client.service.autorizacionComprobante(claveacceso)
            response = client.service.autorizacionComprobante(claveacceso)
        except Exception as e:
            print(e)
            self.write({
                        'estatus_import':'FAIL GET',
                        'fecha_proceso':datetime.now(),
                        'mensajes':('%s')%(e)
                        })
            return False
        autorizaciones = None
        print(response)
        try:
            autorizaciones = response['autorizaciones']['autorizacion'][0]
        except Exception as e:
            self.write({
                        'estatus_import':'FAIL READ',
                        'fecha_proceso':datetime.now(),
                        'mensajes':'Esta tratando de importar un xml sin autorizaciones'
                        })
            return False

        if not autorizaciones:
            self.write({
                        'estatus_import':'FAIL READ',
                        'fecha_proceso':datetime.now(),
                        'mensajes':'Esta tratando de importar un xml sin autorizaciones'
                        })
            return False

        autorizacion = OrderedDict([
            ('autorizacion', OrderedDict([
                ('estado', autorizaciones['estado']),
                ('numeroAutorizacion', autorizaciones['numeroAutorizacion']),
                ('fechaAutorizacion', str(autorizaciones['fechaAutorizacion'])),
                ('ambiente', autorizaciones['ambiente']),
                ('comprobante', u'<![CDATA[{}]]>'.format(
                    autorizaciones['comprobante'])),
            ]))
        ])
        comprobante = xml.sax.saxutils.unescape(
            xmltodict.unparse(autorizacion))

        self.save_xml(comprobante,file_tmp)
        self.write({
                    'estatus_import':'GET',
                    'fecha_proceso':datetime.now(),
                    'mensajes':'Archivo XML descargado desde el SRI'
                    })
        return True


    def receive_de_offline(self, file_tmp):
        ambiente_id = self.ambiente_id #self.env.user.company_id.ambiente_id
        claveacceso = self.name
        try:
            client = Client(ambiente_id.autorizacioncomprobantes)
            with client.settings(raw_response=False):
                response = client.service.autorizacionComprobante(claveacceso)
            response = client.service.autorizacionComprobante(claveacceso)
        except Exception as e:
            print(e)
            self.write({
                        'estatus_import':'FAIL GET',
                        'fecha_proceso':datetime.now(),
                        'mensajes':('%s')%(e)
                        })
            return False
        autorizaciones = None
        print(response)
        try:
            autorizaciones = response['autorizaciones']['autorizacion'][0]
        except Exception as e:
            self.write({
                        'estatus_import':'FAIL READ',
                        'fecha_proceso':datetime.now(),
                        'mensajes':'Esta tratando de importar un xml sin autorizaciones'
                        })
            return False

        if not autorizaciones:
            self.write({
                        'estatus_import':'FAIL READ',
                        'fecha_proceso':datetime.now(),
                        'mensajes':'Esta tratando de importar un xml sin autorizaciones'
                        })
            return False

        autorizacion = OrderedDict([
            ('autorizacion', OrderedDict([
                ('estado', autorizaciones['estado']),
                ('numeroAutorizacion', autorizaciones['numeroAutorizacion']),
                ('fechaAutorizacion', str(autorizaciones['fechaAutorizacion'])),
                ('ambiente', autorizaciones['ambiente']),
                ('comprobante', u'<![CDATA[{}]]>'.format(
                    autorizaciones['comprobante'])),
            ]))
        ])
        comprobante = xml.sax.saxutils.unescape(
            xmltodict.unparse(autorizacion))

        self.save_xml(comprobante,file_tmp)
        self.write({
                    'estatus_import':'GET',
                    'fecha_proceso':datetime.now(),
                    'mensajes':'Archivo XML descargado desde el SRI'
                    })
        return True

    def homologar_lineas_importadas(self):
        if not self.partner_id.email:
            if self.email:
                self.partner_id.email=self.email
            if not self.partner_id.email:
                raise UserError('Debe registrar un correo electronico para el Proveedor!!')

        self.write({
                    'estatus_import':'MAPPING',
                    'fecha_proceso':datetime.now(),
                    'pagina':'2',
                    'pagina_desc':"2",
                    })
        for obj in self:
            obj.mapear_lineas_xml()
            # Si no tiene problemas de homologacion
            if obj.products_to_map_count==0:
                obj.write({
                            'estatus_import':'IMPORT',
                            'fecha_proceso':datetime.now()
                            })
            # Si no tiene problemas de homologacion
            # y es homologacon auto,
            if obj.tipo_homologacion=='auto' and obj.products_to_map_count==0:
                self.action_order_create()

    def mapear_lineas_xml(self):
        for mlinea  in self.compra_detail_ids:
            mlinea.crear_productos_xml()

    def _prepare_purchase_order(self):
        self.ensure_one()
        #journal_id = self.env['account.move'].default_get(['journal_id'])['journal_id']
        #journal_id = self.env['account.journal'].search([('type', '=', 'purchase')], limit=1)

        #if not journal_id:
        #    raise UserError(_('Defina un diario de compras contables para esta empresa.'))
        #strftime( '%Y-%m-%d  %H:%M:%S')
        #print(self.invoice_date.strftime('%Y-%m-%d  %H:%M:%S'))
        mdate1=self.invoice_date.strftime('%Y-%m-%d  %H:%M:%S')
        mdate = datetime.strptime(mdate1, '%Y-%m-%d  %H:%M:%S')
        #mdate = datetime.strptime(self.invoice_date, '%d/%m/%Y').strftime( '%Y-%m-%d')
        order_vals = {
            'edoc_import_id':self.id,
            'partner_ref': self.reference or '',
            'origin': ''+(self.reference or ''),
            'date_order': mdate, #self.invoice_date,
            'date_approve': mdate, #self.invoice_date,
            'partner_id': self.partner_id.id,
            'date_planned':mdate, #self.fechaautorizacion or fields.Date.today(),
            'state':'draft',
            'establecimiento':self.establecimiento,
            'puntoemision':self.puntoemision,
            'secuencial':self.secuencial,
            'autorizacion':self.autorizacion,
            #'fiscal_position_id': self.fiscal_position_id.id or self.partner_id.property_account_position_id.id,
            #'payment_term_id': self.payment_term_id.id,
            #'currency_id': self.currency_id.id,
            #'comment': self.note,
            'company_id': self.company_id.id,
            'total_descuento_xml':self.total_descuento,
            'total_xml':self.total,
            #'user_id': self.user_id and self.user_id.id,
        }

        # Create PO lines if necessary
        xml_importado = self
        compra_detail_lines_tmp = []
        compra_detail_lines = []
        partner = None
        if self.partner_id:
            partner = self.partner_id

        payment_term = partner.property_supplier_payment_term_id

        currency = partner.property_purchase_currency_id or xml_importado.company_id.currency_id

        FiscalPosition = self.env['account.fiscal.position']
        fpos = FiscalPosition.get_fiscal_position(partner.id)
        fpos = FiscalPosition.browse(fpos)
        lines_procesar = xml_importado.compra_detail_ids
        lines_procesar_unir = xml_importado.compra_detail_ids.filtered(lambda lin: lin.unificar == True)
        lines_procesar_distri = xml_importado.compra_detail_ids.filtered(lambda lin: lin.distribuir_code)
        print("**"*5)
        #deja solo las lineas que no tienen condiciones
        for line in lines_procesar-lines_procesar_unir-lines_procesar_distri:
            order_line_values = xml_importado._read_line_info(line,currency,fpos)
            compra_detail_lines_tmp.append(order_line_values)

        for lin in compra_detail_lines_tmp:
            compra_detail_lines.append((0, 0, lin))
        ######## aqui unifica los montos y valores
        res_unir=xml_importado._read_line_info_unir(lines_procesar_unir,fpos)
        print("---  RES UNIR ---")
        print(res_unir)
        print("---"*40)
        for k,d in res_unir:
            price_unit=d['tmp_total']/d['product_qty']
            detalle = xml_importado._prepare_purchase_order_line(
                name=d['name'], product_id=d['product_id'], product_uom_id=d['product_uom'], product_qty=d['product_qty'],
                price_unit=round(price_unit,5), discount = d['discount'],taxes_ids=d['taxes_id'])
            compra_detail_lines.append((0, 0, detalle))

        ######## aqui distribuye a un producto especifico
        res_unir=xml_importado._read_vals_info_distri(lines_procesar_distri)
        print("---  RES DISTRIBUIR ---")
        print(res_unir)
        print("---"*40)
        # values_lines_procesar_distri = []
        for line in lines_procesar_distri:
            vals = xml_importado._read_line_info(line,currency,fpos,res_unir)
            compra_detail_lines.append((0, 0, vals))
            # print(vals['price_unit'])
            # values_lines_procesar_distri.append(vals)
        # print(values_lines_procesar_distri)
        # print(compra_detail_lines)
        order_vals['order_line']=compra_detail_lines
        # raise UserError('PROBANDO!!')
        return order_vals



    def _read_vals_info_distri(self,lines_procesar_distri):
        res = {}
        for line in lines_procesar_distri:
            if line.product_uom != line.product_id.uom_po_id:
                product_qty = line.product_uom._compute_quantity(line.product_qty, line.product_id.uom_po_id)
                price_unit = line.product_uom._compute_price(line.unitario_sin_impuesto, line.product_id.uom_po_id)
            else:
                product_qty = line.product_qty
                price_unit = line.unitario_sin_impuesto

            distribuir_code = line.distribuir_code
            res.setdefault(distribuir_code, {
                'distribuir_code': distribuir_code,
                'product_qty': 0.0,
                'tmp_total':0.0,
                })

            res[distribuir_code]['product_qty'] += product_qty
            res[distribuir_code]['tmp_total'] +=(price_unit*product_qty) #line.total_sin_impuesto #price_unit #round(line.price_unit,4)
        res = sorted(res.items(), key=lambda l: l[0])
        dev_res = {}
        for k,d in res:
            price_unit=d['tmp_total']/d['product_qty']
            distribuir_code = d['distribuir_code']
            dev_res.setdefault(distribuir_code, {
                'distribuir_code': distribuir_code,
                'price_unit': 0.0,
                })
            dev_res[distribuir_code]['price_unit'] += round(price_unit,4)
        return dev_res


    def _read_line_info(self,line,currency,fpos,res_unir=False):
        xml_importado = self
        name = line.product_name
        if fpos:
            taxes_ids = fpos.map_tax(line.supplier_taxes_id.filtered(lambda tax: tax.company_id == xml_importado.company_id)).ids
        else:
            taxes_ids = line.supplier_taxes_id.filtered(lambda tax: tax.company_id == xml_importado.company_id).ids
        # Compute quantity and price_unit
        if line.product_uom != line.product_id.uom_po_id:
            product_qty = line.product_uom._compute_quantity(line.product_qty, line.product_id.uom_po_id)
            price_unit = line.product_uom._compute_price(line.price_unit, line.product_id.uom_po_id)
        else:
            product_qty = line.product_qty
            price_unit = line.price_unit
        # Compute price_unit in appropriate currency
        if xml_importado.company_id.currency_id != currency:
            price_unit = xml_importado.company_id.currency_id.compute(price_unit, currency)
        # Create PO line
        discount = line.discount
        if res_unir:
            price_unit = res_unir[line.distribuir_code]['price_unit'] or 0.0
            discount = 0

        order_line_values = xml_importado._prepare_purchase_order_line(
            name=name, product_id=line.product_id.id, product_uom_id=line.product_id.uom_po_id.id, product_qty=product_qty,
            price_unit=price_unit, discount = discount,taxes_ids=taxes_ids)
        return order_line_values


    def _read_line_info_unir(self,lines_procesar_unir,fpos):
        xml_importado = self
        res = {}
        for line in lines_procesar_unir:
            name = line.product_name
            print()
            if fpos:
                taxes_ids = fpos.map_tax(line.supplier_taxes_id.filtered(lambda tax: tax.company_id == xml_importado.company_id)).ids
            else:
                taxes_ids = line.supplier_taxes_id.filtered(lambda tax: tax.company_id == xml_importado.company_id).ids
            if line.product_uom != line.product_id.uom_po_id:
                product_qty = line.product_uom._compute_quantity(line.product_qty, line.product_id.uom_po_id)
                price_unit = line.product_uom._compute_price(line.price_unit, line.product_id.uom_po_id)
            else:
                product_qty = line.product_qty
                price_unit = line.price_unit

            product_id = line.product_id
            res.setdefault(product_id, {
                'name': "",
                'product_id': product_id.id,
                'product_uom': line.product_id.uom_po_id.id,
                'product_qty': 0.0,
                'price_unit': 0.0,
                'tmp_total':0.0,
                'taxes_id': taxes_ids,
                'discount': 0.0,
                'product_code':line.product_code
                })
            if res[product_id]['product_id']==product_id.id:
                if res[product_id]['product_code']!=line.product_code:
                    res[product_id]['product_qty'] = product_qty
                else:
                    res[product_id]['product_qty'] += product_qty

            res[product_id]['name'] += "  %s"%name
            res[product_id]['tmp_total'] +=(price_unit*product_qty) #line.total_sin_impuesto #price_unit #round(line.price_unit,4)
            res[product_id]['discount'] += round(line.discount,4)
        res = sorted(res.items(), key=lambda l: l[0])
        return res


    def _prepare_purchase_order_line(self, name,product_id,product_uom_id, product_qty=0.0, price_unit=0.0, discount =0.0, taxes_ids=False):
        xml_importado = self
        # discount = self.discount
        if xml_importado.total_descuento_lineas==0.0:
            discount = round(xml_importado.porcentaje_descuento,3)
        return {
            'name': name,
            'product_id': product_id, #self.product_id.id,
            'product_uom': product_uom_id, #self.product_id.uom_po_id.id,
            'product_qty': product_qty,
            'price_unit': price_unit,
            'taxes_id': [(6, 0, taxes_ids)],
            'discount': discount,
            'date_planned': xml_importado.fechaautorizacion or fields.Date.today(),
        }


    def _prepare_purchase_invoice(self):
        self.ensure_one()
        journal = self.env['account.move'].with_context(force_company=self.company_id.id, default_type='in_invoice')._get_default_journal()
        if not journal:
            raise UserError(_('Please define an accounting purchase journal for the company %s (%s).') % (self.company_id.name, self.company_id.id))

        comprobante_id=self.env.ref('l10n_ec_base.comprobante_01')
        #mdate=fields.Date.from_string(self.date_approve)

        invoice_vals = {
            # 'name': self.reference or '',
            'invoice_date':self.invoice_date,
            'fechaemiret1':self.invoice_date,
            'invoice_date':self.invoice_date,
            'comprobante_id':comprobante_id.id,
            'autorizacion' : self.autorizacion or '123456789',
            'establecimiento' : self.establecimiento or '001',
            'puntoemision' : self.puntoemision or '001',
            'secuencial' : self.secuencial or 1,
            'ref': self.reference or '',
            'type': 'in_invoice',
            #'narration': self.notes,
            'invoice_user_id': self.user_id and self.user_id.id,
            'partner_id': self.partner_id.id,
            'fiscal_position_id': self.partner_id.property_account_position_id.id,
            'invoice_origin': 'SRI-'+self.reference,
            'company_id':self.company_id.id,
            #'invoice_payment_term_id': self.payment_term_id.id,
            'edoc_import_id':self.id,
            'total_descuento_xml':self.total_descuento,
            'total_xml':self.total,
            'invoice_line_ids': [],
        }
        return invoice_vals

    def action_order_create(self):
        if not self.partner_id.email:
            raise UserError('Debe registrar un correo electronico para el Proveedor!!')
        purchase_order_obj = self.env['purchase.order']
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        purchase_order = None
        #purchase_order_lines = self.env['purchase.order.line']
        for doc in self:
            order_data = doc._prepare_purchase_order()
            purchase_order = purchase_order_obj.create(order_data)
            for linea in purchase_order.order_line:
                linea._compute_amount()
            if doc.state_purchase_orders=='done':
                purchase_order.button_confirm()
                purchase_order.button_done()
                purchase_order.date_order=self.invoice_date
                purchase_order.date_approve=self.invoice_date
                purchase_order.button_create_invoice()
        if purchase_order:
            self.write({
                        'estatus_cola':'procesado',
                        'estatus_import':'ORDER',
                        'fecha_proceso':datetime.now(),
                        'pagina':'3',
                        'pagina_desc':"3",
                        })
        else:
            return {
                    "type": "ir.actions.do_nothing",
                }

    def action_invoice_create(self):
        if not self.partner_id.email:
            raise UserError('Debe registrar un correo electronico para el Proveedor!!')
        invoice_order = None
        for doc in self:
            invoice_order = doc._create_invoices()
        if invoice_order:
            self.write({
                        'estatus_cola':'procesado',
                        'estatus_import':'INVOICE',
                        'fecha_proceso':datetime.now(),
                        'pagina':'3',
                        'pagina_desc':"3",
                        })
            """
            return {
                'name': invoice_order.name,
                'context': self.env.context,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.move',
                'res_id': invoice_order.id,
                'view_id': False,
                'type': 'ir.actions.act_window',
                #'target': 'new',
            }
            """
        else:
            return {
                    "type": "ir.actions.do_nothing",
                }

    def _create_invoices(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        invoice_vals_list = []
        for order in self:
            #mdate=fields.Date.from_string(order.date_approve)
            invoice_vals = order._prepare_purchase_invoice()
            for line in order.compra_detail_ids:
                if float_is_zero(line.product_qty, precision_digits=precision):
                    continue
                if line.product_qty > 0:
                    invoice_vals['invoice_line_ids'].append((0, 0, line._prepare_invoice_line()))

            if not invoice_vals['invoice_line_ids']:
                raise UserError(_('There is no invoiceable line. If a product has a Delivered quantities invoicing policy, please make sure that a quantity has been delivered.'))

            invoice_vals_list.append(invoice_vals)

        if not invoice_vals_list:
            raise UserError(_(
                'There is no invoiceable line. If a product has a Delivered quantities invoicing policy, please make sure that a quantity has been delivered.'))

        moves = self.env['account.move'].sudo().with_context(default_type='in_invoice').create(invoice_vals_list)

        for move in moves:

            #move.invoice_date = mdate
            for line in move.invoice_line_ids:
                line._onchange_price_subtotal()
                # line._compute_all()
            move._compute_amount()
            #move.message_post_with_view('mail.message_origin_link',
            #    values={'self': move, 'origin': move.line_ids.mapped('sale_line_ids.order_id')},
            #    subtype_id=self.env.ref('mail.mt_note').id
            #)
        return moves


class ImportElectronicDetails(models.Model):
    _name = "l10n_ec_base.edoc.import.details"
    _description = "Detalle de Importación de Documentos Electrónicos"

    def _get_default_uom_id(self):
        return self.env["uom.uom"].search([], limit=1, order='id').id

    def _get_iva_taxes_bye_type(self,codigoPorcentaje):
        # Obtiene los impuesto que corresponden al IVA, codigo = 2
        # codigoPorcentaje = 0 : IVA 0
        # codigoPorcentaje = 1 : IVA 12

        ICPSudo = self.env['ir.config_parameter'].sudo()
        default_sale_tax_id = None
        default_purchase_tax_id = None
        if codigoPorcentaje=='0': #IVA 0
            if self.type=='product' or self.type==False:
                #productos iva 0
                default_sale_tax_id = literal_eval(ICPSudo.get_param('product0_sale_tax_id', default='False'))
                default_purchase_tax_id = literal_eval(ICPSudo.get_param('product0_purchase_tax_id', default='False'))
            if self.type=='service':
                #servicios iva
                default_sale_tax_id = literal_eval(ICPSudo.get_param('service0_sale_tax_id', default='False'))
                default_purchase_tax_id = literal_eval(ICPSudo.get_param('service0_purchase_tax_id', default='False'))
            if self.type=='consu':
                #conumibles iva
                default_sale_tax_id = literal_eval(ICPSudo.get_param('consu0_sale_tax_id', default='False'))
                default_purchase_tax_id = literal_eval(ICPSudo.get_param('consu0_purchase_tax_id', default='False'))
        elif codigoPorcentaje=='2': #IVA 12
            if self.type=='product' or self.type==False:
                #productos iva
                default_sale_tax_id = literal_eval(ICPSudo.get_param('product_sale_tax_id', default='False'))
                default_purchase_tax_id = literal_eval(ICPSudo.get_param('product_purchase_tax_id', default='False'))
            if self.type=='service':
                #servicios iva
                default_sale_tax_id = literal_eval(ICPSudo.get_param('service_sale_tax_id', default='False'))
                default_purchase_tax_id = literal_eval(ICPSudo.get_param('service_purchase_tax_id', default='False'))
            if self.type=='consu':
                #conumibles iva
                default_sale_tax_id = literal_eval(ICPSudo.get_param('consu_sale_tax_id', default='False'))
                default_purchase_tax_id = literal_eval(ICPSudo.get_param('consu_purchase_tax_id', default='False'))

        #Si no esta codigoPorcentaje en 1 ó 0 toma los impuestos por defeecto de Flectra
        if not default_sale_tax_id:
            IrDefault = self.env['ir.default'].sudo()
            default_sale_tax_id = IrDefault.get('product.template', "taxes_id", company_id=self.company_id.id or self.env.user.company_id.id)

        if not default_purchase_tax_id:
            IrDefault = self.env['ir.default'].sudo()
            default_purchase_tax_id = IrDefault.get('product.template', "supplier_taxes_id", company_id=self.company_id.id or self.env.user.company_id.id)

        return default_sale_tax_id,default_purchase_tax_id

    def _get_taxes_default(self,taxes_line):
        taxes =[]
        taxes_sale =[]

        #detalle = comprobante['factura']['detalles']['detalle']
        _una_sola_linea = False
        try:
            m=taxes_line['codigo']
            _una_sola_linea = True
        except:
            _una_sola_linea = False
            #info_lineas['detalle']=[info_lineas['detalle']]


        if _una_sola_linea:
            taxes_line=[taxes_line]

        for _tax in taxes_line:
            if _tax['codigo']=='2': #IVA
                sale_tax_id,purchase_tax_id = self._get_iva_taxes_bye_type(_tax['codigoPorcentaje'])
                taxes_sale.append(sale_tax_id)
                taxes.append(purchase_tax_id)
            else: # busca el impuesto en el listado general de impuesto, usa codido y codigoporcentaje
                table_obj = self.env['account.tax']
                mrecord = None
                mrecord = table_obj.search([
                    ('codigo','=',_tax['codigo']),
                    ('codigoporcentaje','=',_tax['codigoPorcentaje']),
                    ('type_tax_use','=','purchase'),
                    #('tax_group_id','=',4)
                    ], limit=1)

                if mrecord:
                    taxes.append(mrecord.id)
                else:
                    self.compra_id.write({
                                'estatus_import':'FAIL READ',
                                'fecha_proceso':datetime.now(),
                                'mensajes':'Impuesto no encontrado: %s'%(_tax)
                                })

        return taxes_sale,taxes


    @api.onchange('type')
    def _onchange_type(self):

        if not self.impuestos:
            return
        taxes =[]
        taxes_sale =[]
        _impuestos = eval(self.impuestos)
        for _impuesto in _impuestos:
            tax_sale,tax = self._get_taxes_default(_impuesto)
            taxes_sale = tax_sale
            taxes=tax
        taxes=taxes[0]
        taxes_sale=taxes_sale[0]
        if not isinstance(taxes, list):
            taxes=[taxes]
        if not isinstance(taxes_sale, list):
            taxes_sale=[taxes_sale]
        self.supplier_taxes_id=[( 6, 0, taxes)]
        self.customer_taxes_id=[( 6, 0, taxes_sale)]


    def _get_default_category_id(self):

        ICPSudo = self.env['ir.config_parameter'].sudo()
        product_categ_id = literal_eval(ICPSudo.get_param('l10n_ec_base.product_categ_id', default='False'))
        service_categ_id = literal_eval(ICPSudo.get_param('l10n_ec_base.service_categ_id', default='False'))
        consu_categ_id = literal_eval(ICPSudo.get_param('l10n_ec_base.consu_categ_id', default='False'))

        # print(product_categ_id)

        if self.type=='service':
            if service_categ_id:
                return service_categ_id

        if self.type=='consu':
            if consu_categ_id:
                return consu_categ_id

        if product_categ_id:
            return product_categ_id

        if self._context.get('product_categ_id') or self._context.get('default_product_categ_id'):
            return self._context.get('product_categ_id') or self._context.get('default_product_categ_id')
        category = self.env.ref('product.product_category_all', raise_if_not_found=False)
        if not category:
            category = self.env['product.category'].search([], limit=1)
        if category:
            return category.id
        else:
            err_msg = _('You must define at least one product category in order to be able to create products.')
            redir_msg = _('Go to Internal Categories')
            raise RedirectWarning(err_msg, self.env.ref('product.product_category_action_form').id, redir_msg)


    #_order = 'sequence, product_qty desc, price_unit'
    name = fields.Text(string='Descripcion', required=False)
    sequence = fields.Integer('Sequence', default=1)
    compra_id = fields.Many2one('l10n_ec_base.edoc.import', string='Factura de Compra',ondelete='cascade', index=True)
    product_name = fields.Char('Nombre')
    product_code = fields.Char('Código')
    product_uom = fields.Many2one('uom.uom', 'Unidad',default=_get_default_uom_id, required=True)
    product_tmpl_id = fields.Many2one('product.template', 'Product Template',index=True, ondelete='cascade')
    product_qty = fields.Float('Cantidad', default=0.0, required=True)
    price_unit = fields.Float('Precio', default=0.0, digits=(12,5))
    discount = fields.Float(string='Desc (%)', digits=(12,2),default=0.0)
    monto_discount = fields.Float(string='Monto Desc', digits=(12,2),default=0.0)
    total_sin_impuesto = fields.Float(string='totalSinImpuesto', digits='Product Price',default=0.0)
    unitario_sin_impuesto = fields.Float(string='unitarioSinImpuesto', digits='Product Price',default=0.0)
    pvp_empaque = fields.Float('Precio de Venta', default=0.0, digits=(12,5))
    company_id = fields.Many2one('res.company', 'Company',default=lambda self: self.env.user.company_id.id, index=1)
    tracking = fields.Selection([
        ('serial', 'Serie'),
        #('lot', 'Por Lotes'),
        ('none', 'No')], string="Seguimiento", default='none', required=True)

    customer_taxes_id = fields.Many2many('account.tax', 'import_taxes_rel', 'detail_id', 'tax_id', string='Impuestos Ventas',
        domain=[('type_tax_use', '=', 'sale')])
    supplier_taxes_id = fields.Many2many('account.tax', 'taxes_supplier_taxes_rel', 'detail_id', 'tax_id', string='Impuestos Compras',
        domain=[('type_tax_use', '=', 'purchase')])

    crear = fields.Boolean(default=False)
    unificar = fields.Boolean(default=False)
    distribuir = fields.Boolean(default=False)
    distribuir_code = fields.Char('Codigo producto para Distribución')

    # type = fields.Selection([
    #     ('consu', 'Consumible'),
    #     ('service','Servicio'),
    #     ('product','Almacenable')
    #     ], string='Tipo', default='product', required=True)
    type = fields.Selection(
        string="Tipo",
        selection=[
            ('consu', "Goods"),
            ('service', "Service"),
            ('combo', "Combo"),
        ],
        required=True,
        default='consu',
    )
    categ_id = fields.Many2one('product.category', 'Categoria',change_default=True, default=_get_default_category_id)
    product_id = fields.Many2one('product.product', string='Producto', domain=[('purchase_ok', '=', True)], change_default=True, ondelete='cascade')

    tipo_homologacion = fields.Selection(
        [
            ('auto', 'Homologación automática'),
            ('manual', 'Homologación manual')
            ],
        related='compra_id.tipo_homologacion', string='Tipo de Homologación', readonly=True, copy=False, store=True, default='manual')
    impuestos = fields.Char('Impuestos')
    dummie = fields.Char("")



    def _prepare_invoice_line(self):
        self.ensure_one()
        #if self.currency_id == move.company_id.currency_id:
        #    currency = False
        #else:
        #    currency = move.currency_id
        fiscal_position =  self.compra_id.partner_id.property_account_position_id
        accounts = self.product_id.product_tmpl_id.get_product_accounts(fiscal_pos=fiscal_position)
        account_id = accounts['expense']
        compra = self.compra_id
        taxes_ids = self.supplier_taxes_id.filtered(lambda tax: tax.company_id == compra.company_id).ids
        return {
            'sequence': self.sequence,
            'name': '%s: %s' % (self.product_name, self.product_id.name),
            #'purchase_line_id': self.id,
            'product_uom_id': self.product_uom.id or self.product_id.uom_po_id.id,
            'product_id': self.product_id.id,
            'price_unit': self.price_unit,
            'quantity': self.product_qty,
            'discount':self.discount,
            #'analytic_account_id': self.account_analytic_id.id,
            #'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],

            #'tax_ids': [(6, 0, self.taxes_id.ids)],
            'tax_ids': [(6, 0, taxes_ids)],
            'account_id':account_id.id
        }




    def button_asignar_producto_linea(self):
        for rec in self:
            if rec.compra_id.product_id:
                rec.product_id=rec.compra_id.product_id
                rec.product_tmpl_id=rec.compra_id.product_id.product_tmpl_id
                rec.crear_codes_prov_xml()
                rec.supplier_taxes_id=rec.product_id.supplier_taxes_id
                rec.customer_taxes_id=rec.product_id.taxes_id
            else:
                raise UserError("Necesita seleccionar un producto para asignar")


    def button_asignar_segimiento_linea(self):
        for rec in self:
            if not rec.product_id:
                if rec.tracking=='none':
                    rec.tracking='serial'
                else:
                    rec.tracking='none'

    # taxes_id = fields.Many2many('account.tax', 'product_taxes_rel', 'prod_id', 'tax_id', help="Default taxes used when selling the product.", string='Customer Taxes',
    #     domain=[('type_tax_use', '=', 'sale')], default=lambda self: self.env.company.account_sale_tax_id)
    # supplier_taxes_id = fields.Many2many('account.tax', 'product_supplier_taxes_rel', 'prod_id', 'tax_id', string='Vendor Taxes', help='Default taxes used when buying the product.',
    #     domain=[('type_tax_use', '=', 'purchase')], default=lambda self: self.env.company.account_purchase_tax_id)

    def button_crear_producto_desde_linea(self):
        self.ensure_one()
        for rec in self:
            supplier_code= rec.verifica_codes_supplier_prov_xml()
            product_code= rec.verifica_codes_prod_prov_xml()
            if supplier_code:
                rec.product_id=supplier_code.product_id
            elif product_code:
                rec.product_id=product_code.id
            else:
                if rec.type=='product':
                    if len(rec.customer_taxes_id)==0:
                        rec.customer_taxes_id=self.env.company.account_sale_tax_id
                    if len(rec.supplier_taxes_id)==0:
                        rec.supplier_taxes_id=self.env.company.account_purchase_tax_id
                else:
                    if len(rec.customer_taxes_id)==0:
                        raise UserError("Debe seleccionar los impuestos de Compras para continuar")
                    if len(rec.supplier_taxes_id)==0:
                        raise UserError("Debe seleccionar los impuestos de Ventas para continuar")

                rec.crear= True
                rec.crear_productos_xml()
            if rec.product_id:
                rec.compra_id.update({'product_id':rec.product_id.id})


    def button_crear_producto_linea(self):
        self.ensure_one()
        for rec in self:
            supplier_code= rec.verifica_codes_supplier_prov_xml()
            product_code= rec.verifica_codes_prod_prov_xml()
            if supplier_code:
                rec.product_id=supplier_code.product_id
            elif product_code:
                rec.product_id=product_code.id
            else:
                rec.crear= False #True  Se cambio ahora es manual
                rec.crear_productos_xml()
            if rec.product_id:
                rec.compra_id.update({'product_id':rec.product_id.id})

    def button_borrar_linea(self):
        self.ensure_one()
        for rec in self:
            rec.unlink()


    def crear_codes_prov_xml(self):
        mcode = None
        mcode = self.env['product.supplierinfo'].search([
            ('name', '=', self.compra_id.partner_id.id),
            ('product_code', '=', self.product_code)
            ], limit=1)

        if mcode:
            print("mcode  1111 >>> ",mcode)
            if not mcode.product_tmpl_id==self.product_tmpl_id:
                mcode = None
            if mcode:
                mcode.write({'unificar':self.unificar,'distribuir':self.distribuir,'distribuir_code':self.distribuir_code})
        if not mcode:
            if self.product_tmpl_id:
                vals_codes={
                'name':self.compra_id.partner_id.id,
                'product_name':self.product_name,
                'product_code':self.product_code,
                'product_uom':self.product_uom.id,
                'product_tmpl_id':self.product_tmpl_id.id,
                'product_id':self.product_id.id,
                'unificar':self.unificar,
                'distribuir':self.distribuir,
                'distribuir_code':self.distribuir_code,
                }
                mcode = self.env['product.supplierinfo'].create(vals_codes)
                self.crear=False
        return mcode

    def verifica_codes_supplier_prov_xml(self):
        mcode = None
        mcode = self.env['product.supplierinfo'].search([
            ('name', '=', self.compra_id.partner_id.id),
            ('product_code', '=', self.product_code)
            ], limit=1)
        return mcode

    def verifica_codes_prod_prov_xml(self):
        mcode = None
        mcode = self.env['product.product'].search([
            ('default_code', '=', self.product_code)
            ], limit=1)
        return mcode

    def crear_productos_xml(self):
        self.ensure_one()

        if self.crear:
            vals ={
            'name':self.product_name,
            'default_code':'/', #self.product_code,
            'uom_id':self.env.ref('uom.product_uom_unit').id,
            'uom_po_id':self.product_uom.id,
            'list_price':self.pvp_empaque,
            'categ_id':self.categ_id.id,
            'standard_price':self.unitario_sin_impuesto,
            'type':self.type,
            'purchase_ok':True,
            'sale_ok':True,
            'tracking':self.tracking
            }

            vals['supplier_taxes_id']=[( 6, 0, self.supplier_taxes_id.ids)]
            vals['taxes_id']=[( 6, 0, self.customer_taxes_id.ids)]

            mproducto = self.env['product.product'].create(vals)
            if mproducto:
                self.product_tmpl_id.bar_code =self.product_code
                self.product_id = mproducto.id
                self.product_tmpl_id = mproducto.product_tmpl_id.id

                mtemplate =  mproducto.product_tmpl_id
                if mtemplate:
                    mtemplate.tracking=self.tracking
        else:
            mproducto= self.product_tmpl_id
        if mproducto:
            self.crear_codes_prov_xml()
            self.supplier_taxes_id=self.product_id.supplier_taxes_id
            self.customer_taxes_id=self.product_id.taxes_id
        return mproducto


    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.product_tmpl_id=self.product_id.product_tmpl_id.id


    @api.onchange('product_tmpl_id')
    def _onchange_product_tmpl_id(self):
        product_tmpl = self.product_tmpl_id
        if product_tmpl:
            self.pvp_empaque=product_tmpl.lst_price
            self.categ_id=product_tmpl.categ_id.id
            self.type = product_tmpl.type
            self.crear = False
            self.tracking = product_tmpl.tracking
        else:
            self.pvp_empaque=self.price_unit*1.20
            self.categ_id=self._get_default_category_id()
            self.type = 'product'
            self.crear = False # Antes esta True para permitir crear automaticamente, ahora debe ser manual
            self.tracking ='none'
