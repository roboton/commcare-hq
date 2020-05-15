import textwrap

from custom.inddex import filters
from custom.inddex.const import ConvFactorGaps, FctGaps
from custom.inddex.food import FoodData

from .utils import MultiTabularReport, format_row


class GapsDetailReport(MultiTabularReport):
    name = 'Output 2b - Detailed Information on Gaps'
    slug = 'gaps_detail'
    is_released = False
    description = textwrap.dedent("""
        This output assists researchers in identifying incomplete or missing
        information in the recall data. Researchers can use this output to view the
        specific items reported by respondents that are missing conversion factor or
        food composition data. This output also includes the information collected from
        the respondent during the recall. All gaps in this report should be addressed
        before researchers conduct data analysis. Researchers therefore should not
        download Outputs 3 and 4 unless all gaps in this report have been addressed.
    """)

    @property
    def fields(self):
        return [
            filters.CaseOwnersFilter,
            filters.DateRangeFilter,
            filters.GapDescriptionFilter,
            filters.FaoWhoGiftFoodGroupDescriptionFilter,
            filters.FoodTypeFilter,
            filters.RecallStatusFilter,
        ]

    @property
    def data_providers(self):
        food_data = FoodData.from_request(self.domain, self.request)
        return [
            GapsByItemSummaryData(food_data),
            GapsDetailsData(food_data)
        ]


class GapsByItemSummaryData:
    title = 'Gaps By Item Summary'
    slug = 'gaps_by_item_summary'
    headers = [
        'food_code', 'food_name', 'fao_who_gift_food_group_code',
        'fao_who_gift_food_group_description', 'user_food_group', 'food_type',
        'number_occurrence', 'conv_factor_gap_code',
        'conv_factor_gap_desc', 'fct_gap_code', 'fct_gap_desc'
    ]

    def __init__(self, food_data):
        self._food_data = food_data

    @property
    def rows(self):
        rows = {}
        for row in self._food_data.rows:
            if row.conv_factor_gap_code != ConvFactorGaps.AVAILABLE:
                key = (row.food_name, row.conv_method_code, row.conv_factor_gap_code)
                if key not in rows:
                    rows[key] = {col: getattr(row, col) for col in self.headers if col != 'number_occurrence'}
                    rows[key]['number_occurrence'] = 1
                else:
                    rows[key]['number_occurrence'] += 1

        for row in rows.values():
            yield format_row([row[col] for col in self.headers])


class GapsDetailsData:
    title = 'Gaps By Item Details'
    slug = 'gaps_by_item_details'
    headers = [
        'gap_type', 'gap_code', 'gap_desc', 'food_type', 'caseid', 'food_code',
        'food_name', 'short_name', 'eating_time', 'time_block',
        'fao_who_gift_food_group_code', 'fao_who_gift_food_group_description',
        'user_food_group', 'food_base_term', 'tag_1', 'other_tag_1', 'tag_2',
        'other_tag_2', 'tag_3', 'other_tag_3', 'tag_4', 'other_tag_4', 'tag_5',
        'other_tag_5', 'tag_6', 'other_tag_6', 'tag_7', 'other_tag_7', 'tag_8',
        'other_tag_8', 'tag_9', 'other_tag_9', 'tag_10', 'other_tag_10',
        'conv_method_code', 'conv_method_desc', 'conv_option_code',
        'conv_option_desc', 'measurement_amount', 'conv_units', 'portions',
        'nsr_conv_method_code_post_cooking', 'nsr_conv_method_desc_post_cooking',
        'nsr_conv_option_code_post_cooking', 'nsr_conv_option_desc_post_cooking',
        'nsr_measurement_amount_post_cooking', 'nsr_consumed_cooked_fraction',
        'conv_factor_used', 'conv_factor_food_code',
        'conv_factor_base_term_food_code', 'fct_data_used',
        'fct_food_code_exists', 'fct_base_term_food_code_exists',
        'fct_reference_food_code_exists', 'base_term_food_code',
        'reference_food_code', 'unique_respondent_id', 'recall_case_id',
        'opened_by_username', 'owner_name', 'visit_date'
    ]

    def __init__(self, food_data):
        self._food_data = food_data

    @property
    def rows(self):
        for row in self._food_data.rows:
            for gap_class, gap_code in [
                    (ConvFactorGaps, row.conv_factor_gap_code),
                    (FctGaps, row.fct_gap_code),
            ]:
                if (self._food_data.selected_gap_type in [None, gap_class.slug]
                        and gap_code != gap_class.AVAILABLE):
                    manually_set = ['gap_type', 'gap_code', 'gap_desc']
                    yield format_row([gap_class.name, gap_code, gap_class.get_description(gap_code)] + [
                        getattr(row, col) for col in self.headers if col not in manually_set
                    ])
