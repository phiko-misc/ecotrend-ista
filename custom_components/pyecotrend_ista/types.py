# numpydoc ignore=EX01
"""Typed response structures for the DK EcoTrend API."""

from typing import TypeAlias, TypedDict


class TokenResponse(TypedDict):  # numpydoc ignore=ES01,SA01,EX01
    """
    Represents the Token response in the ista EcoTrend DK API.

    Attributes
    ----------
    access_token : str
        The access token for the API.
    token_type : str
        The type of token.
    expires_in : str
        The number of seconds until the token expires.
    ".issued" : str
        The timestamp when the token was issued.
    ".expires" : str
        The timestamp when the token expires.
    Email : str
        The email address associated with the token.
    Phone : str
        The phone number associated with the token.
    FirstName : str
        The first name associated with the token.
    InstanceId : str
        The instance ID associated with the token.
    Language : str
        The language associated with the token.
    Username : str
        The username associated with the token.
    PortalAdminId : str
        The portal admin ID associated with the token.
    ConsId : str
        The consumer ID associated with the token.
    isTenant : str
        Indicates whether the token is for a tenant.
    InstId : str
        The installation ID associated with the token.
    isAdmin : str
        Indicates whether the token is for an admin user.
    Key : str
        The key associated with the token.
    """

    access_token: str
    token_type: str
    expires_in: str
    issued: str
    expires: str
    Email: str
    Phone: str
    FirstName: str
    InstanceId: str
    Language: str
    Username: str
    PortalAdminId: str
    ConsId: str
    isTenant: str
    InstId: str
    isAdmin: str
    Key: str

class UserInfo(TypedDict):  # numpydoc ignore=ES01,SA01,EX01
    """
    Represents the response for an user info in the ista EcoTrend DK API.

    Attributes
    ----------
    Username : str
        The username of the account holder.
    Name : str
        The full name of the account holder.
    Phone : str
        The phone number of the account holder.
    Email : str
        The email address of the account holder.
    Language : str
        The language preference of the account holder.
    Address : str
        The address of the account holder.
    ZipCity : str
        The zip code and city of the account holder.
    ShowEconomy : bool
        Indicates whether to show economy information.
    ShowClimate : bool
        Indicates whether to show climate information.
    """

    Username: str
    Name: str
    Phone: str
    Email: str
    Language: str
    Address: str
    ZipCity: str
    ShowEconomy: bool
    ShowClimate: bool

class UserSettings(TypedDict):  # numpydoc ignore=ES01,SA01,EX01
    """
    Represents the response for an user settings in the ista EcoTrend DK API.

    Attributes
    ----------
    Mail : str
        The email address of the account holder.
    Phone : str
        The phone number of the account holder.
    UseDayValues : bool
        Indicates whether to use day values.
    UseHourValues : bool
        Indicates whether to use hour values.
    TenantCount : int
        The number of tenants in the account.
    PreferredProgram : int
        The preferred program for the account holder.
    receiveNotification : bool
        Indicates whether to receive notifications.
    receiveNotificationByMail : bool
        Indicates whether to receive notifications by mail.
    receiveNotificationByPhone : bool
        Indicates whether to receive notifications by phone.
    """

    Mail: str
    Phone: str
    UseDayValues: bool
    UseHourValues: bool
    TenantCount: int
    PreferredProgram: int
    receiveNotification: bool
    receiveNotificationByMail: bool
    receiveNotificationByPhone: bool

class MetersErrorMessage(TypedDict):  # numpydoc ignore=ES01,SA01,EX01
    """
    Represents the Meters error response in the ista EcoTrend DK API.

    Attributes
    ----------
    ErrorType : str
        The type of error.
    UserMessage : str
        The user-friendly error message.
    InternalMessage : str
        The internal error message.
    """

    ErrorType: str
    UserMessage: str
    InternalMessage: str

class MetersValue(TypedDict):  # numpydoc ignore=ES01,SA01,EX01
    """
    Represents the Meters value in the ista EcoTrend DK API.

    Attributes
    ----------
    Message : str | None
        The message associated with the meter value.
    Headline : str | None
        The headline associated with the meter value.
    MeterText : str
        The text associated with the meter.
    MeterType : str
        The type of meter.
    Unit : str
        The unit of measurement for the meter value.
    INST_NO : int
        The installation number of the meter.
    Last_Meter_Reading : int
        The last reading of the meter.
    Reading_date : str | None
        The date of the last reading of the meter.
    Last_Meter_Consumption : int
        The last consumption value of the meter.
    METER_ID : int
        The ID of the meter.
    ROOM_DESCR : str
        The description of the room where the meter is installed.
    METER_NO : str
        The number of the meter.
    METCAT_LABEL : str
        The label of the meter category.
    METTYPE_CODE : str | None
        The code of the meter type.
    Deactivation_date : str
        The deactivation date of the meter.
    Activation_date : str
        The activation date of the meter.
    """

    Message: None | str
    Headline: None | str
    MeterText: str
    MeterType: str
    Unit: str
    INST_NO: int
    Last_Meter_Reading: int
    Reading_date: None | str
    Last_Meter_Consumption: int
    METER_ID: int
    ROOM_DESCR: str
    METER_NO: str
    METCAT_LABEL: str
    METTYPE_CODE: None | str
    Deactivation_date: str
    Activation_date: str

class MetersValues(TypedDict):  # numpydoc ignore=ES01,SA01,EX01
    """
    TypedDict represents the Meters Values in the ista EcoTrend DK API.

    Attributes
    ----------
    value : list[MetersValue]
        The list of meter values.
    """

    value: list[MetersValue]

class MetersResponse(TypedDict):  # numpydoc ignore=ES01,SA01,EX01
    """
    Represents the Meters response in the ista EcoTrend DK API.

    Attributes
    ----------
    errorMessage : MetersErrorMessage
        The error message associated with the meter response.
    Meters : MetersValues
        The list of meter values associated with the meter response.
    """

    errorMessage: MetersErrorMessage
    Meters: MetersValues

class MeterTypesCompare(TypedDict):  # numpydoc ignore=ES01,SA01,EX01
    """
    A TypedDict representing the Meter Types Compare in the ista EcoTrend DK graphs API.

    Attributes
    ----------
    comparePeriode : bool
        Indicates whether the comparison is for a period.
    property : bool
        Indicates whether the comparison is for a property.
    installation : bool
        Indicates whether the comparison is for an installation.
    national : bool
        Indicates whether the comparison is national.
    outsideTemperature : bool
        Indicates whether the comparison includes outside temperature.
    aconto : bool
        Indicates whether the comparison includes aconto (advance payment).
    """

    comparePeriode: bool
    property: bool
    installation: bool
    national: bool
    outsideTemperature: bool
    aconto: bool

class MeterTypesInterval(TypedDict):  # numpydoc ignore=ES01,SA01,EX01
    """
    A TypedDict representing the Meter Types interval in the ista EcoTrend DK graphs API.

    Attributes
    ----------
    hour : bool
        Indicates whether the interval is hourly.
    day : bool
        Indicates whether the interval is daily.
    week : bool
        Indicates whether the interval is weekly.
    month : bool
        Indicates whether the interval is monthly.
    year : bool
        Indicates whether the interval is yearly.
    """

    hour: bool
    day: bool
    week: bool
    month: bool
    year: bool

class MeterTypesElement(TypedDict):  # numpydoc ignore=ES01,SA01,EX01
    """
    A TypedDict representing the Meter Types interval in the ista EcoTrend DK graphs API.

    Attributes
    ----------
    unit : str
        The unit of measurement for the meter type element.
    useEcoData : bool
        Indicates whether eco data is used for the meter type element.
    interval : MeterTypesInterval
        The interval settings for the meter type element.
    compare : MeterTypesCompare
        The comparison settings for the meter type element.
    """

    unit: str
    useEcoData: bool
    interval: MeterTypesInterval
    compare: MeterTypesCompare

class MeterTypesResponse(TypedDict):  # numpydoc ignore=ES01,SA01,EX01
    """
    Represents the Meter Types response in the ista EcoTrend DK graphsAPI.

    Attributes
    ----------
    electricity : MeterTypesElement | None
        The meter type element for electricity, or None if not available.
    heat : MeterTypesElement | None
        The meter type element for heat, or None if not available.
    waterCold : MeterTypesElement | None
        The meter type element for cold water, or None if not available.
    waterHot : MeterTypesElement | None
        The meter type element for hot water, or None if not available.
    energy : MeterTypesElement | None
        The meter type element for energy, or None if not available.
    co2 : MeterTypesElement | None
        The meter type element for CO2, or None if not available.
    humidity : MeterTypesElement | None
        The meter type element for humidity, or None if not available.
    noise : MeterTypesElement | None
        The meter type element for noise, or None if not available.
    temperature : MeterTypesElement | None
        The meter type element for temperature, or None if not available.
    temperatureOut : MeterTypesElement | None
        The meter type element for outside temperature, or None if not available.
    humonic : MeterTypesElement | None
        The meter type element for humonic, or None if not available.
    """

    electricity: MeterTypesElement | None
    heat: MeterTypesElement | None
    waterCold: MeterTypesElement | None
    waterHot: MeterTypesElement | None
    energy: MeterTypesElement | None
    co2: MeterTypesElement | None
    humidity: MeterTypesElement | None
    noise: MeterTypesElement | None
    temperature: MeterTypesElement | None
    temperatureOut: MeterTypesElement | None
    humonic: MeterTypesElement | None



class ElectricityConsumptionElement(TypedDict):  # numpydoc ignore=ES01,SA01,EX01
    """
    TypedDict representing the electricity and consumption element in the ista EcoTrend DK Graphs API.

    Attributes
    ----------
    when : str
        The time period for the consumption element.
    value : int | None
        The consumption value for the specified time period, or None if not available.
    formerPeriode : float | None
        The consumption value for the former period, or None if not available.
    minValue : int | None
        The minimum consumption value for the specified time period, or None if not available.
    maxValue : float | None
        The maximum consumption value for the specified time period, or None if not available.
    percent : float | None
        The percentage change in consumption compared to the former period, or None if not available.
    property : float | None
        The property value associated with the consumption, or None if not available.
    propertyProcentage : float | None
        The percentage change in property value compared to the former period, or None if not available.
    national : float | None
        The national average consumption value, or None if not available.
    nationalProcentage : float | None
        The percentage change in national average consumption compared to the former period, or None if not available.
    corresponding : float | None
        The corresponding consumption value for the same period in the previous year, or None if not available.
    price : float | None
        The price associated with the consumption, or None if not available.
    cumulativePrice : float
        The cumulative price for the consumption up to the specified time period.
    aconto : float | None
        The aconto (advance payment) amount associated with the consumption, or None if not available.
    date : str
        The date associated with the consumption element.
    stopDate : str | None
        The stop date for the consumption element, or None if not available.
    interval : int
        The interval for the consumption element (e.g., hourly, daily).
    outsideTemperature : float | None
        The outside temperature associated with the consumption element, or None if not available.
    headline : str
        The headline or title for the consumption element.
    dateValueTemplate : str
        The template for displaying the date and value of the consumption element.
    message : str
        The message or description associated with the consumption element.
    seriesSetup : str | None
        The series setup information for the consumption element, or None if not available.
    periodeFrom : str | None
        The start date of the period for the consumption element, or None if not available.
    periodeTo : str | None
        The end date of the period for the consumption element, or None if not available.
    priceValue : int | None
        The price value associated with the consumption, or None if not available.
    """

    when: str
    value: int | None
    formerPeriode: float | None
    minValue: int | None
    maxValue: float | None
    percent: float | None
    property: float | None
    propertyProcentage: float | None
    national: float | None
    nationalProcentage: float | None
    corresponding: float | None
    price: float | None
    cumulativePrice: float
    aconto: float | None
    date: str
    stopDate: str | None
    interval: int
    outsideTemperature: float | None
    headline: str
    dateValueTemplate: str
    message: str
    seriesSetup: str | None
    periodeFrom: str | None
    periodeTo: str | None
    priceValue: int | None

ElectricityConsumptionResponse: TypeAlias = list[ElectricityConsumptionElement]  # numpydoc ignore=ES01,SA01,EX01
"""Represent the response for economy and consumption elements from the ista EcoTrend DK Graphs API."""