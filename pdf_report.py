# pdf_report.py
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os


class PDFReportGenerator:
    """增强版PDF报告生成器（含封面、页脚、优化排版）"""

    def __init__(self):
        # 尝试注册中文字体
        try:
            font_paths = [
                "C:/Windows/Fonts/simhei.ttf",
                "C:/Windows/Fonts/msyh.ttc",
                "C:/Windows/Fonts/simsun.ttc",
                "/System/Library/Fonts/PingFang.ttc",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
            ]
            for font_path in font_paths:
                if os.path.exists(font_path):
                    pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                    self.font_name = 'ChineseFont'
                    break
            else:
                self.font_name = 'Helvetica'
        except:
            self.font_name = 'Helvetica'

        self.styles = getSampleStyleSheet()
        self._setup_styles()

    def _setup_styles(self):
        """设置报告样式"""
        self.styles.add(ParagraphStyle(
            name='ChineseTitle',
            fontName=self.font_name,
            fontSize=28,
            textColor=colors.HexColor('#1a5276'),
            alignment=1,
            spaceAfter=30
        ))
        self.styles.add(ParagraphStyle(
            name='CoverTitle',
            fontName=self.font_name,
            fontSize=36,
            textColor=colors.HexColor('#2C4A3E'),
            alignment=1,
            spaceAfter=20,
            bold=True
        ))
        self.styles.add(ParagraphStyle(
            name='CoverSubtitle',
            fontName=self.font_name,
            fontSize=18,
            textColor=colors.HexColor('#5C7A6E'),
            alignment=1,
            spaceAfter=10
        ))
        self.styles.add(ParagraphStyle(
            name='ChineseHeading',
            fontName=self.font_name,
            fontSize=16,
            textColor=colors.HexColor('#2980b9'),
            spaceBefore=15,
            spaceAfter=10,
            bold=True
        ))
        self.styles.add(ParagraphStyle(
            name='ChineseBody',
            fontName=self.font_name,
            fontSize=11,
            leading=18,
            textColor=colors.HexColor('#2c3e50')
        ))
        self.styles.add(ParagraphStyle(
            name='ChineseSmall',
            fontName=self.font_name,
            fontSize=9,
            textColor=colors.HexColor('#7f8c8d')
        ))
        self.styles.add(ParagraphStyle(
            name='FooterStyle',
            fontName=self.font_name,
            fontSize=8,
            textColor=colors.HexColor('#95a5a6'),
            alignment=1
        ))
        # 风险等级样式
        self.styles.add(ParagraphStyle(
            name='RiskRed',
            fontName=self.font_name,
            fontSize=14,
            textColor=colors.HexColor('#c0392b'),
            alignment=1
        ))
        self.styles.add(ParagraphStyle(
            name='RiskYellow',
            fontName=self.font_name,
            fontSize=14,
            textColor=colors.HexColor('#e67e22'),
            alignment=1
        ))
        self.styles.add(ParagraphStyle(
            name='RiskBlue',
            fontName=self.font_name,
            fontSize=14,
            textColor=colors.HexColor('#2980b9'),
            alignment=1
        ))
        self.styles.add(ParagraphStyle(
            name='RiskGreen',
            fontName=self.font_name,
            fontSize=14,
            textColor=colors.HexColor('#27ae60'),
            alignment=1
        ))

    def get_risk_style(self, risk_level):
        if risk_level == "高风险":
            return 'RiskRed', '#c0392b'
        elif risk_level == "中风险":
            return 'RiskYellow', '#e67e22'
        elif risk_level == "低风险":
            return 'RiskBlue', '#2980b9'
        else:
            return 'RiskGreen', '#27ae60'

    def _add_page_number_and_footer(self, canvas, doc):
        """添加页脚（页码 + 版权信息）"""
        canvas.saveState()
        # 页脚文字
        footer_text = "© 2025 心语团队 - 心理健康预警系统"
        canvas.setFont(self.font_name, 8)
        canvas.setFillColor(colors.HexColor('#95a5a6'))
        # 居中绘制页脚文字
        page_width = A4[0]
        canvas.drawCentredString(page_width / 2, 20 * mm, footer_text)
        # 页码
        page_num = canvas.getPageNumber()
        canvas.drawRightString(page_width - 20 * mm, 20 * mm, f"第 {page_num} 页")
        canvas.restoreState()

    def _build_cover(self, user_name):
        """构建封面故事流"""
        story = []
        # 加一些空白推动封面内容到视觉中心
        story.append(Spacer(1, 80 * mm))

        # 主标题
        story.append(Paragraph("心理健康评估报告", self.styles['CoverTitle']))
        story.append(Spacer(1, 10 * mm))

        # 副标题
        story.append(Paragraph("—— 心语智能体 · 温柔守护每一份情绪", self.styles['CoverSubtitle']))
        story.append(Spacer(1, 30 * mm))

        # 用户信息表格
        info_data = [
            ["用户姓名", user_name],
            ["报告生成日期", datetime.now().strftime("%Y年%m月%d日")],
            ["报告编号", f"XINYU-{datetime.now().strftime('%Y%m%d%H%M')}"]
        ]
        info_table = Table(info_data, colWidths=[80 * mm, 80 * mm])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#5C7A6E')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#2C3E50')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F4F7F5')),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#BDC3C7')),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 20 * mm))

        # 温情提示
        story.append(Paragraph("本报告由 AI 智能分析生成，仅供参考，不能替代专业医疗诊断。", self.styles['ChineseSmall']))
        story.append(Paragraph("如有需要，请拨打心理援助热线：12356", self.styles['ChineseSmall']))

        # 封面结束，插入分页
        story.append(PageBreak())
        return story

    def generate_report(self, user_name, report_data):
        """
        生成PDF报告
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            topMargin=25 * mm,
            bottomMargin=25 * mm,
            leftMargin=20 * mm,
            rightMargin=20 * mm
        )

        story = []

        # ========== 封面页 ==========
        story.extend(self._build_cover(user_name))

        # ========== 正文标题 ==========
        story.append(Paragraph("详细评估数据", self.styles['ChineseTitle']))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#2980b9')))
        story.append(Spacer(1, 10))

        # ========== 基础信息 ==========
        story.append(Paragraph("基础信息", self.styles['ChineseHeading']))
        info_data = [
            ["用户姓名", user_name],
            ["报告生成时间", datetime.now().strftime("%Y年%m月%d日 %H:%M")],
            ["追踪周期", f"{report_data.get('total_days', 14)}天"]
        ]
        info_table = Table(info_data, colWidths=[60 * mm, 100 * mm])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#7f8c8d')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#2c3e50')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 15))

        # ========== 风险概览 ==========
        story.append(Paragraph("风险概览", self.styles['ChineseHeading']))

        risk_style, risk_color = self.get_risk_style(report_data.get('risk_desc', '正常'))

        story.append(Paragraph(
            f"当前风险等级：<font color='{risk_color}'><b>{report_data.get('risk_desc', '正常')}</b></font>",
            self.styles['ChineseBody']
        ))
        story.append(Paragraph(
            f"风险综合评分：{report_data.get('risk_score', 0):.1%}",
            self.styles['ChineseBody']
        ))
        story.append(Spacer(1, 10))

        # 风险指标表格
        metrics_data = [
            ["负面情绪比例", f"{report_data.get('negative_ratio', 0):.1f}%"],
            ["恶化趋势", f"{report_data.get('worsening_trend', 0):.1f}%"],
            ["连续负面天数", f"{report_data.get('consecutive_bad', 0)}天"],
            ["危机信号", "有" if report_data.get('has_crisis') else "无"]
        ]
        metrics_table = Table(metrics_data, colWidths=[60 * mm, 60 * mm])
        metrics_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f3f5')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#2980b9')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(metrics_table)
        story.append(Spacer(1, 15))

        # ========== 情绪分布 ==========
        story.append(Paragraph("情绪分布统计", self.styles['ChineseHeading']))

        emotion_counts = report_data.get('emotion_counts', {})
        total_records = report_data.get('total_records', 1)
        emotion_data = [
            ["情绪类型", "出现次数", "占比"],
            ["快乐", str(emotion_counts.get('快乐', 0)), f"{emotion_counts.get('快乐', 0) / total_records * 100:.1f}%"],
            ["平静", str(emotion_counts.get('平静', 0)), f"{emotion_counts.get('平静', 0) / total_records * 100:.1f}%"],
            ["焦虑", str(emotion_counts.get('焦虑', 0)), f"{emotion_counts.get('焦虑', 0) / total_records * 100:.1f}%"],
            ["悲伤", str(emotion_counts.get('悲伤', 0)), f"{emotion_counts.get('悲伤', 0) / total_records * 100:.1f}%"],
            ["愤怒", str(emotion_counts.get('愤怒', 0)), f"{emotion_counts.get('愤怒', 0) / total_records * 100:.1f}%"]
        ]
        emotion_table = Table(emotion_data, colWidths=[45 * mm, 45 * mm, 45 * mm])
        emotion_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2980b9')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
        ]))
        story.append(emotion_table)
        story.append(Spacer(1, 15))

        # ========== 近期情绪记录 ==========
        story.append(Paragraph("近期情绪记录", self.styles['ChineseHeading']))

        daily_emotions = report_data.get('daily_emotions', [])
        if daily_emotions:
            recent_7 = daily_emotions[-7:] if len(daily_emotions) > 7 else daily_emotions
            emotion_data = [["日期", "情绪"]]
            for date, emotion in recent_7:
                emotion_data.append([date, emotion])

            daily_table = Table(emotion_data, colWidths=[60 * mm, 60 * mm])
            daily_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2980b9')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
            ]))
            story.append(daily_table)
        else:
            story.append(Paragraph("暂无足够数据", self.styles['ChineseBody']))

        story.append(Spacer(1, 15))

        # ========== 综合建议 ==========
        story.append(Paragraph("综合建议", self.styles['ChineseHeading']))

        advice = report_data.get('advice', '继续保持良好的生活习惯，关注自己的情绪变化。')
        story.append(Paragraph(advice, self.styles['ChineseBody']))
        story.append(Spacer(1, 15))

        # ========== 求助信息 ==========
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#2980b9')))
        story.append(Spacer(1, 10))
        story.append(Paragraph(
            "<font color='#7f8c8d'>如有需要，请拨打心理援助热线：12356</font>",
            self.styles['ChineseSmall']
        ))

        # 生成PDF，并传入页脚绘制函数
        doc.build(story, onFirstPage=self._add_page_number_and_footer, onLaterPages=self._add_page_number_and_footer)
        buffer.seek(0)
        return buffer


def generate_report_pdf(user_name, report_data):
    """生成PDF报告的便捷函数"""
    generator = PDFReportGenerator()
    return generator.generate_report(user_name, report_data)